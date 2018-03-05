# CH<sub>4</sub> polarizability with turbo-lanzos

* convert `CH4-pw.xml` to namelist input for pw  and run self-consistent calculation 
```
../../../qespresso/utils/xml2qeinput.py -in CH4-pw.xml
pw.x < CH4-pw.in
```

*  convert `CH4.tddfpt.xml` in namelist format and run turbo-lanzos.x calculation 
```
../../../qespresso/utils/xml2qeinput.py -in CH4-tddfpt.xml
turbo_lanczos.x < CH4-tddfpt.in 
```

* convert `CH4.tddfpt_pp.xml` in namelist format and run turbo_spectrum.x calculation
```
../../../qespresso/utils/xml2qeinput.py -in CH4.tddfpt_pp.xml
turbo_spectrum.x < CH4.tddfpt_pp.in 
```
* Polarizabilty tensor and Oscillator strength as function of energy are given in `CH4.plot_chi.dat` file  
