# Diff-Jjoules Demo

This project aims at showing how Diff-JJoules works and what can be done.

## Diff-JJoules

Diff-JJoules aims at measuring the impact of code changes (commit) on energy consumption.

The algorithm is as follow : 

1. Clone twice the project
2. Each clone is set to a specific version, for example two successive commits
3. Execute the tests on the two versions and select the tests as follow :
    * Select the tests in the version before the commit that execute the lines that have been removed by the commit
    * Select the tests in the version after the commit that execute the lines that have been added by the commit
4. Instrument the tests that have been selected with special annotations to measure the energy consumption of each test
5. Execute the instrumented tests on the two versions
6. Observe the difference of tests' energy consumption program's version-wise; This difference approximate the impact of the commit on the global energy comsumption.

## Prerequisites

:construction:
### Install JAVA 11

### Install TLPC-Sensor

You need to install [libpfm4](https://github.com/gfieni/libpfm4)

```sh
git clone https://github.com/davidson-consulting/tlpc-sensor
cd tlpc-sensor/examples/tlpc-sensor
mvn clean install -DskipTests
```

### Install DSpot-diff-test-selection

```sh
git clone https://github.com/STAMP-project/dspot.git
cd dspot
mvn clean install -DskipTests
```

### Install Diff-JJoules

```sh
git clone https://github.com/davidson-consulting/diff-jjoules
cd diff-jjoules
mvn clean install -DskipTests
cd diff-jjoules-maven
mvn clean install -DskipTests
```

### Set up permission to RAPL and perf_event

```sh
sudo chmod -R 777 /sys/devices/virtual/powercap/intel-rapl/intel-rapl:*
sudo -i
echo -1 > /proc/sys/kernel/perf_event_paranoid
```

### Configure Compilation for Warming up the JVM with Maven (Optionnal, slow down the demo)

```sh
export MAVEN_OPTS="-XX:CompileThreshold=1 -XX:-TieredCompilation"
```

## Demo

### Scenario

In this demo, the code changes is an artificial increase of the execution time of a method:

```diff
public void methodOne() {
    consume(2000);
+    consume(2000);
}
```

### Instrumentation Example

:construction:

### Run 

To run the demo, you need to first clone twice this repository:

```sh
git clone https://github.com/davidson-consulting/diff-jjoules-demo.git /tmp/v1
git clone https://github.com/davidson-consulting/diff-jjoules-demo.git /tmp/v2
```

Then, checkout the `v2` to the correct version:

```sh
cd v2
git checkout demo
```

Eventually, run `diff-jjoules`:

```sh
cd /tmp/v1
mvn fr.davidson:diff-jjoules-maven:diff-jjoules -Dpath-dir-second-version=/tmp/v2/ -Dsuspect=false
```
