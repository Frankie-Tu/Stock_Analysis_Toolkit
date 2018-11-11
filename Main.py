
from Scrappers.Main import ScrapperApp
import pandas
import pdb

# --------------------------------------------------------------------
mymain = ScrapperApp(['dol.to', 'ctc-a.to', 'MRU.to', 'ATD-B.TO', 'SAP.TO',
                     'L.TO', 'EMP-A.TO','mfi.to'],
                     foldername='Retail', comprehensive=True,
                     filesave=True)
mymain.scrapper_start()

mymain = ScrapperApp(['rei-un.to','hr-un.to','d-un.to','car-un.to', 'Ap-un.to', 'ax-un.to','csh-un.to','bei-un.to',
                      'cuf-un.to','crr-un.to','bip-un.to','fcr.to'],
                     foldername='Reit', comprehensive=True,
                     filesave=True)
mymain.scrapper_start()

mymain = ScrapperApp(['ala.to','h.to','enb.to','fts.to','ema.to','aqn.to','npi.to','ine.to','rnw.to','cpx.to',
                      'trp.to','cp.to'],
                     foldername='Utilities', comprehensive=True,
                     filesave=True)
mymain.scrapper_start()

mymain = ScrapperApp(['bns.to','bmo.to','cm.to','ry.to','na.to','td.to','bam-a.to','mfc.to','slf.to','pwf.to',
                      'ifc.to','pow.to'],
                     foldername='Banks', comprehensive=True,
                     filesave=True)
mymain.scrapper_start()

mymain = ScrapperApp(['goos.to','shop.to','Gib-a.to'],
                     foldername='Interesting', comprehensive=True,
                     filesave=True)
mymain.scrapper_start()

mymain = ScrapperApp(['fts.to','npi.to','cpx.to','rnw.to','trp.to','cp.to','l.to','sap.to',
                      'atd-b.to','ctc-a.to','mru.to','fcr.to','ap-un.to','car-un.to','hr-un.to',
                      'rei-un.to','bam-a.to','na.to','ry.to','cm.to','bns.to'],
                     foldername='EVERYTHING', comprehensive=True,
                     filesave=True)
mymain.scrapper_start()







