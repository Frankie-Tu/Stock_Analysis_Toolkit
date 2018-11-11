from Scrappers.Main import ScrapperApp

# --------------------------------------------------------------------
mymain = ScrapperApp(['dol.to', 'ctc-a.to', 'MRU.to', 'ATD-B.TO', 'SAP.TO',
                     'L.TO', 'EMP-A.TO'],
                     foldername='Retail', comprehensive=True,
                     filesave=False)
mymain.scrapper_start()

mymain = ScrapperApp(['rei-un.to','hr-un.to','d-un.to','car-un.to','fcr.to'],
                     foldername='Reit', comprehensive=True,
                     filesave=False)
mymain.scrapper_start()

mymain = ScrapperApp(['ala.to','h.to','enb.to','fts.to','ema.to','aqn.to','npi.to','ine.to','rnw.to','cpx.to'],
                     foldername='Utilities', comprehensive=True,
                     filesave=False)
mymain.scrapper_start()

mymain = ScrapperApp(['bns.to','bmo.to','cm.to','ry.to','na.to','td.to'],
                     foldername='Banks', comprehensive=True,
                     filesave=False)
mymain.scrapper_start()

