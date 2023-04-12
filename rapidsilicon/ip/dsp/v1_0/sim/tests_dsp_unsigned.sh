#!/bin/bash
# Start of for loop
current_dir=$PWD
dsp_sim=$DSP_SIM
a=72
b=0
for i in {1..72}
do
    a=$(($a))
    b=$(($b + 1))
    aa=$(($a - 1))
    bb=$(($b - 1))
    c=$(($aa + $bb + 1))
    (echo -e  "A = $a\t\tB =$b\t\tFeature=BASE" && ../dsp_gen.py --build --a_width=$a --b_width=$b
    cd rapidsilicon/ip/dsp/v1_0/dsp_wrapper/
    sed -i "s/\[71:0\]a/\[$aa:0\]a/g" sim/dsp_test.v
    sed -i "s/\[6:0\]b/\[$bb:0\]b/g" sim/dsp_test.v
    sed -i "s/\[78:0\]z1/\[$c:0\]z1/g" sim/dsp_test.v
    sed -i "s/\[78:0\]z/\[$c:0\]z/g" sim/dsp_test.v
    sed -i "s/a <= {20{1'b1}}/a <= {$a{1'b1}}/g" sim/dsp_test.v
    sed -i "s/b <= {20{1'b1}}/b <= {$b{1'b1}}/g" sim/dsp_test.v
    sed -i "s/a <= {20{1'b0}}/a <= {$a{1'b0}}/g" sim/dsp_test.v
    sed -i "s/b <= {20{1'b0}}/b <= {$b{1'b0}}/g" sim/dsp_test.v
    iverilog src/*.v sim/*.v $dsp_sim -g2012 -o dsp && vvp dsp) 2>&1 | tee -a dsp_tests_unsigned.log
    cd $current_dir
done

a=68
b=0
for i in {1..68}
do
    a=$(($a))
    b=$(($b + 1))
    aa=$(($a - 1))
    bb=$(($b - 1))
    c=$(($aa + $bb + 1))
    (echo -e  "A = $a\t\tB =$b\t\tFeature=ENHANCED" && ../dsp_gen.py --build --a_width=$a --b_width=$b --feature=Enhanced
    cd rapidsilicon/ip/dsp/v1_0/dsp_wrapper/
    sed -i "s/\[71:0\]a/\[$aa:0\]a/g" sim/dsp_test.v
    sed -i "s/\[6:0\]b/\[$bb:0\]b/g" sim/dsp_test.v
    sed -i "s/\[78:0\]z1/\[$c:0\]z1/g" sim/dsp_test.v
    sed -i "s/\[78:0\]z/\[$c:0\]z/g" sim/dsp_test.v
    sed -i "s/a <= {20{1'b1}}/a <= {$a{1'b1}}/g" sim/dsp_test.v
    sed -i "s/b <= {20{1'b1}}/b <= {$b{1'b1}}/g" sim/dsp_test.v
    sed -i "s/a <= {20{1'b0}}/a <= {$a{1'b0}}/g" sim/dsp_test.v
    sed -i "s/b <= {20{1'b0}}/b <= {$b{1'b0}}/g" sim/dsp_test.v
    iverilog src/*.v sim/*.v $dsp_sim -g2012 -o dsp && vvp dsp) 2>&1 | tee -a dsp_tests_unsigned.log
    cd $current_dir
done

for i in {1..72}
do
    a=$[ $RANDOM % 52 + 20 ]
    b=$[ $RANDOM % 52 + 20 ]
    aa=$(($a - 1))
    bb=$(($b - 1))
    c=$(($aa + $bb + 1))
    (echo -e  "A = $a\t\tB =$b\t\tFeature=PIPELINE" && ../dsp_gen.py --build --a_width=$a --b_width=$b --feature=Pipeline
    cd rapidsilicon/ip/dsp/v1_0/dsp_wrapper/
    sed -i "s/\[71:0\]a/\[$aa:0\]a/g" sim/dsp_test.v
    sed -i "s/\[6:0\]b/\[$bb:0\]b/g" sim/dsp_test.v
    sed -i "s/\[78:0\]z1/\[$c:0\]z1/g" sim/dsp_test.v
    sed -i "s/\[78:0\]z/\[$c:0\]z/g" sim/dsp_test.v
    sed -i "s/a <= {20{1'b1}}/a <= {$a{1'b1}}/g" sim/dsp_test.v
    sed -i "s/b <= {20{1'b1}}/b <= {$b{1'b1}}/g" sim/dsp_test.v
    sed -i "s/a <= {20{1'b0}}/a <= {$a{1'b0}}/g" sim/dsp_test.v
    sed -i "s/b <= {20{1'b0}}/b <= {$b{1'b0}}/g" sim/dsp_test.v
    if [ $a -gt 54 ] || [ $b -gt 54 ]
    then
        sed -i "s/repeat (1) @ (posedge clk1)/repeat (4) @ (posedge clk1)/g" sim/dsp_test.v
    elif [ $a -gt 36 ] || [ $b -gt 36 ]
    then
        sed -i "s/repeat (1) @ (posedge clk1)/repeat (3) @ (posedge clk1)/g" sim/dsp_test.v
    elif [ $a -gt 18 ] || [ $b -gt 18 ]
    then
        sed -i "s/repeat (1) @ (posedge clk1)/repeat (2) @ (posedge clk1)/g" sim/dsp_test.v
    fi
    sed -i "s/.a(a),.b(b),.z(z2)/.a(a1),.b(b1),.z(z2)/g" sim/dsp_test.v
    sed -i "s/.a(a),.b(b),.z(z1)/.a(a),.b(b),.z(z1), .clk(clk1), .reset(reset)/g" sim/dsp_test.v
    sed -i "s/#2000/#5000/g" sim/dsp_test.v
    iverilog src/*.v sim/*.v $dsp_sim -g2012 -o dsp && vvp dsp) 2>&1 | tee -a dsp_tests_unsigned.log
    cd $current_dir
done

if grep -iq "error" ./dsp_tests_unsigned.log; then
    echo -e  "Simulation Failed\n" 2>&1 | tee -a dsp_tests_unsigned.log
fi
if ! grep -iq "error" ./dsp_tests_unsigned.log; then
    echo -e  "Simulation Passed\n" 2>&1 | tee -a dsp_tests_unsigned.log
fi