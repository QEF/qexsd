# Ag EELS simulation with turbo\_eels

* convert `Ag.xml` to namelist input for pw  and run self-consistent calculation 
```
../../../qespresso/utils/xml2qeinput.py -in Ag.xml
pw.x < Ag.in
```

*  convert `Ag.tddfpt-eels.xml` in namelist format and run turbo\_eels.x calculation 
```
../../../qespresso/utils/xml2qeinput.py -in Ag.tddfpt-eels.xml
turbo_eels.x < Ag.tddfpt-eels.in 
```

* convert `Ag.tddfpt_pp.xml` in namelist format and run turbo\_spectrum.x calculation
```
../../../qespresso/utils/xml2qeinput.py -in Ag.tddfpt_pp.xml
turbo_spectrum.x < Ag.tddfpt_pp.in
```
 
