#!/usr/bin/env python3
import os, glob, argparse
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

def flux_to_mag(flux):
    f = np.array(flux, dtype=float)
    mag = np.full_like(f, np.nan, dtype=float)
    m = f > 0
    mag[m] = 27.5 - 2.5*np.log10(f[m])
    return mag

def detect_mask(snr, photflag=None):
    det = snr >= 5.0
    if photflag is not None:
        pf = photflag.astype(int)
        det = np.logical_or(det, (pf & 4096) > 0)
        det = np.logical_or(det, (pf & 16384) > 0)
    return det

def read_fits_lc(phot_fits):
    with fits.open(phot_fits) as hdul:
        t = hdul['PHOT'].data
        mjd = np.array(t['MJD'], float)
        flux = np.array(t['FLUXCAL'], float)
        fluxerr = np.array(t['FLUXCALERR'], float)
        band = np.char.decode(t['BAND']) if t['BAND'].dtype.kind in ['S','U'] else t['BAND'].astype(str)
        band = np.array([b.strip() for b in band])
        photflag = t['PHOTFLAG'] if 'PHOTFLAG' in t.columns.names else None
        z = hdul[0].header.get('REDSHIFT_CMB', None)
        mwebv = hdul[0].header.get('MWEBV', None)
        peak = hdul[0].header.get('PEAKMJD', None)
    return mjd, flux, fluxerr, band, photflag, z, mwebv, peak

def plot_one(mjd, flux, fluxerr, band, title="", z=None, mwebv=None, peakmjd=None):
    snr = np.where(fluxerr>0, flux/fluxerr, 0.0)
    det = detect_mask(snr)
    fig, ax = plt.subplots(figsize=(6,3))
    for b in ['u','g','r','i','z','Y']:
        m = (band == b)
        if not np.any(m): continue
        md, fd, ed = mjd[m], flux[m], fluxerr[m]
        dmask = det[m]
        ax.errorbar(md[dmask], fd[dmask], yerr=ed[dmask], fmt='o', ms=3, lw=0.8, label=f'{b} det', alpha=0.9)
        ax.errorbar(md[~dmask], fd[~dmask], yerr=ed[~dmask], fmt='o', ms=3, lw=0.8, label=f'{b} non det', alpha=0.5, color='gray')
    ax.axhline(0, ls=':', lw=0.8, color='k', alpha=0.5)
    ax.set_xlabel('MJD (días)'); ax.set_ylabel('Flujo (μJ)')
    hdr=[]
    if z is not None: hdr.append(f"z: {float(z):.4f}")
    if mwebv is not None: hdr.append(f"mwebv: {float(mwebv):.4f}")
    if peakmjd is not None: hdr.append(f"peakmjd: {float(peakmjd):.6f}")
    if hdr: title = (title + "  " + ", ".join(hdr)).strip()
    ax.set_title(title, fontsize=10)
    # leyenda compacta
    handles, labels = ax.get_legend_handles_labels()
    seen = set(); h2,l2=[],[]; kept_non=False
    for h,l in zip(handles,labels):
        if l.endswith('det'):
            b = l.split()[0]
            if b not in seen:
                seen.add(b); h2.append(h); l2.append(l)
        elif (not kept_non) and l.endswith('non det'):
            kept_non=True; h2.append(h); l2.append('non det')
    ax.legend(h2,l2, ncol=4, fontsize=8, frameon=False)
    fig.tight_layout()
    return fig

def main():
    ap = argparse.ArgumentParser(description="Graficar LCs de muestra y histogramas combinados (PHOT.FITS).")
    ap.add_argument('--sndata-root', required=True, help='Ruta SNDATA_ROOT (contiene SIM/GENVERSION/...)')
    ap.add_argument('--pattern', required=True, help="Patrón de GENVERSION (ej: 'SNIax_20241202_*of50')")
    ap.add_argument('--outdir', required=True, help='Carpeta salida')
    ap.add_argument('--max-plots-per-gen', type=int, default=2, help='Curvas de luz de muestra por GENVERSION')
    args = ap.parse_args()

    sim_base = os.path.join(args.sndata_root, 'SIM')
    gen_dirs = sorted([p for p in glob.glob(os.path.join(sim_base, args.pattern)) if os.path.isdir(p)])
    if not gen_dirs:
        raise SystemExit(f"No encontré carpetas con patrón {args.pattern} en {sim_base}")

    os.makedirs(args.outdir, exist_ok=True)

    all_peakmag, all_z = [], []

    for gen in gen_dirs:
        phot_files = sorted(glob.glob(os.path.join(gen, '*_PHOT.FITS')))
        cnt = 0
        for f in phot_files[:args.max_plots_per_gen]:
            mjd, flux, fluxerr, band, photflag, z, mwebv, peak = read_fits_lc(f)
            fig = plot_one(mjd, flux, fluxerr, band, title=os.path.basename(gen), z=z, mwebv=mwebv, peakmjd=peak)
            outpng = os.path.join(args.outdir, os.path.basename(f).replace('.FITS','.png'))
            fig.savefig(outpng, dpi=160); plt.close(fig)

            snr = np.where(fluxerr>0, flux/fluxerr, 0.0)
            det = detect_mask(snr, photflag)
            mag = flux_to_mag(flux)
            if np.any(det) and np.any(np.isfinite(mag[det])):
                all_peakmag.append(np.nanmin(mag[det]))
            if (z is not None) and np.any(det):
                all_z.append(float(z))
            cnt += 1
        print(f"{os.path.basename(gen)} → {cnt} LCs guardadas")

    # Histogramas combinados
    if all_z:
        plt.figure(figsize=(5,3))
        bins = np.linspace(0, max(0.05, max(all_z)), 30)
        plt.hist(all_z, bins=bins, alpha=0.85)
        plt.xlabel('Redshift (detectados)'); plt.ylabel('N'); plt.title('Distribución de z (combinada)')
        plt.tight_layout(); plt.savefig(os.path.join(args.outdir,'hist_redshift_detectados_all.png'), dpi=160); plt.close()
    if all_peakmag:
        pm = np.array(all_peakmag, float)
        plt.figure(figsize=(5,3))
        bins = np.linspace(np.nanmin(pm)-0.2, np.nanmax(pm)+0.2, 30)
        plt.hist(pm, bins=bins, alpha=0.85)
        plt.xlabel('Magnitud pico (detectados)'); plt.ylabel('N'); plt.title('Distribución de magnitud pico (combinada)')
        plt.gca().invert_xaxis()
        plt.tight_layout(); plt.savefig(os.path.join(args.outdir,'hist_peakmag_detectados_all.png'), dpi=160); plt.close()

if __name__ == '__main__':
    main()
