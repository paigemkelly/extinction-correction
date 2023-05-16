import pyneb as pn
from argparse import ArgumentParser
import yaml
import numpy as np

parser = ArgumentParser()
parser.add_argument('config_file', help='the filename of the config to run')

class Config:
    def __init__(self, args):
        """Opens configuration file."""
        self.filename = args.config_file
        with open(self.filename, 'r') as stream:
            self._config = yaml.safe_load(stream)
        return

    # Methods used to access values/keys from config.
    def __getitem__(self, key):
        return self._config[key]

    def __setitem__(self, key, value):
        self._config[key] = value

    def __delitem__(self, key):
        del self._config[key]

    def __contains__(self, key):
        return key in self._config

    def __len__(self):
        return len(self._config)

    def __repr__(self):
        return repr(self._config)

class E_BV:
    def __init__(self,config_file):

        config = config_file
        self.wave_other = config["wave_other"]
        self.f_HB = config["flux_H_beta"]
        self.f_other = config["flux_other"]
        self.wave_HB = config["wave_H_beta"]
        self.curve = config["dust_curve"]
        self.int_ratio = config["intrinsic_ratio"]
        self.color_excess(config_file)
        return
    def calzetti_attenuation_curve(self,wave):
        wavelength = wave*10**(-4)
        if  0.63 <= wavelength <= 2.20 :
            k = 2.659*(-1.857 + 1.040/wavelength) + 4.05
            return k
        elif  0.12 <= wavelength <= 0.63:
            k = 2.659*(-2.156 + 1.509/wavelength - 0.198/(wavelength**2) + 0.011/(wavelength**3)) + 4.05
            return k
        else:
            print ("wavelength out of range :(")

    def cardelli_attenuation_curve(self,wave):
        x = 1/(wave*10**(-4)) # units of 1/micrometer
        #Rv = Av/E(b-v) & k = Alambda/E(b-v)
        if 0.3 < x < 1.1 :
            Rv = 3.1
            a = 0.574*x**(1.61)
            b = -0.527*x**(1.41)
            Al_by_Av = a + b/Rv
            k = Rv*Alambda_by_Av
            return k

        if 1.1 < x < 3.3 :
            Rv = 3.1
            y = x - 1.82
            a = 1 + 0.17699*y - 0.50447*y**2 - 0.02427*y**3 + 0.72085*y**4 + 0.01979*y**5 - 0.77530*y**6 + 0.32999*y**7
            b= 1.41338*y + 2.28305*y**2 + 1.07233*y**3 - 5.38434*y**4 - 0.62251*y**5 + 5.30260*y**6 - 2.09002*y**7
            Alambda_by_Av = a + b/Rv
            k = Rv*Alambda_by_Av
            return k
        else:
            print("wavelength out of range :()")

    def color_excess(self,config):
        if self.curve == "calzetti":
            print("using calzetti curve...")
            self.k_other = self.calzetti_attenuation_curve(self.wave_other)
            self.k_HB = self.calzetti_attenuation_curve(self.wave_HB)
            self.E = -2.5*np.log10((self.f_other/self.f_HB)/self.int_ratio)/(self.k_other-self.k_HB)
            print("c:", 0.4*self.E*self.k_HB)
            rc = pn.RedCorr(E_BV = self.E, R_V = 3.1, law = 'CCM89')
            print("red corrected:", rc)
            return self.E
        elif self.curve == "cardelli":
            print("using cardelli curve...")
            self.k_other = self.cardelli_attenuation_curve(self.wave_other)
            self.k_HB = self.cardelli_attenuation_curve(self.wave_HB)
            self.E = -2.5*np.log10((self.f_other/self.f_HB)/self.int_ratio)/(self.k_other-self.k_HB)
            print("c:", 0.4*self.E*self.k_HB)
            rc = pn.RedCorr(E_BV = self.E, R_V = 3.1, law = 'CCM89')
            print("red corrected:", rc)
            return self.E
        else:
            print("invalid curve")
            return

def main():
    args = parser.parse_args()
    config = Config(args)
    E = E_BV(config)
    return
if __name__ == '__main__':
    main()
