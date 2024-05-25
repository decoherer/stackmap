# stackmap
Create a 2D cross-sectional view of the stack for each step in the lithography process (a.k.a. process flow diagram)
~~~python
    L = Stackmap(-20,20,-5,15)
    L.addlayer(5,name='quartz')
    L.addlayer(3,name='silicon 3µm')
    L.deposit(0.5,'positive resist 0.5µm')
    L.exposeanddevelop(0.5,[np.nan,5,10,5,np.nan],mask=+1)
    L.masketch(1.5)
    L.deposit(1,'metal 1µm')
    L.liftoff()
    L.addlayer(2,name='SiO₂ 2µm')
    L.plot()
~~~
![stackmap example 06](https://github.com/decoherer/stackmap/assets/63128649/c8ef3bb1-4c63-430f-8b9d-14e7ed93971e)
