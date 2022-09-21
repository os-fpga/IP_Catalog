import os
import logging
import site


logger = logging.getLogger('IP Catalog')

logging.basicConfig(level=logging.INFO)

logger.info('Dependency Check for IP Generation')

try:
    from litex.build.osfpga import OSFPGAPlatform
    logger.info('Litex/Migen installed, Good to go')
except ImportError:
    logger.error('Litex is not available, make sure you have litex installed')
    logger.info('To get litex visit https://github.com/enjoy-digital/litex')
#    exit


print(site.USER_SITE)
print(site.getusersitepackages())

src = site.getusersitepackages()

for root, dirs, files in os.walk(src):
    for file in files:
        if file.startswith('litex'):
            print (root+'/'+str(file))
        if file.startswith('migen'):
            print (root+'/'+str(file))


