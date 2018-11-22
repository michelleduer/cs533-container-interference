### CPU Benchmarking
***

##### Test Cases
* Baseline Tests:
  * *_baseline1_*: Single container running Linpack, limited to 2 CPUs
  * *_baseline2_*: Single container runs unrestricted with Linpack running
  * *_baseline3_*: Run Linpack natively
  * *_baseline4_*: Single ontainer with Linpack under 200%, limited to 2 CPUs
  
 * Multi-Core Tests:
 
   (*Linpack Paramters*: 1000 equations, 1000 leading dimension, 500 trials, 64 alignment)
   
   * *_Linpack vs. Linpack_*
     * *_lvl1_*: Container running Linpack & container running Linpack, no restrictions on CPU usage
     * *_lvl2_*: Container running Linpack & container running Linpack, restricting CPU usage (2 CPU)

   * *_Linpack vs. stress_*
     * *_lvs1_*: Container running Linpack & container running stress, no restrictions on CPU usage
     * *_lvs2_*: Container running Linpack & container running stress, restricting CPU usage (2 CPU)

 
 * Reduced Linpack Tests:
 
   (*Reduced Linpack Paramters*: 500 equations, 1000 leading dimension, 500 trials, 64 alignment)
   
   * *_reduced1_*: Container running Linpack <100%, container running Linpack, no restrictions
   * *_reduced2_*: Container running Linpack <100%, container running Linpack, both restricted 2-CPU 
   * *_reduced3_*: Container running Linpack <100% (restricted 2-CPU), native running Linpack
   * *_reduced4_*: Container running Linpack <100%, Container running Linpack <100% (restricted 2-CPU)
   * *_reduced5_*: Container running Linpack <100%, container running Linpack <100% no restrictions
   

##### cpu_benchmarking.py
* Builds Linpack benchmark and stress images
* Creates Docker containers with relevant images per test
* runs test cases and stores results as logfiles
* stops/cleans remnant containers


##### graph.py
* graphs data in logfiles by converting data to CSVs and using seaborn's barplot


##### Dockerfile.lp and linpack_benchmark.sh
* creates a docker container with the Linpack benchmark by running the associated script


##### Dockerfile.st and stress_benchmark.sh
* creates a docker container with the stress test by running the associated script


##### requirements.txt
* to install the necessary libraries, run the following command:
```pip install -r requirements.txt```


##### lessons and WIP (given more time)
* the **threading** library used in the multi-core and reduced Linpack tests did not work for parallelism. The **multiprocessing** library should be used to implement the parallel processes to fix this. These specific tests had to be run manually.
* clean-up redundant code in the test cases
* running more experiments with a more diverse set of Linpack parameters and deeper knowledge of the equations

