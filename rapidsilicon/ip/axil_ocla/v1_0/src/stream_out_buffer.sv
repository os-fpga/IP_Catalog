
//////////////////////////////////////////////////////////////////////////////////
// Company: Rapid Silicon
// Engineer: Zafar Ali
// 
// Create Date: 10/17/2022 04:34:13 PM
// Design Name: OCLA -  
// Module Name: stream_out_buffer 
// Project Name: On-Chip Logic Analyzer Soft IP Development
// Target Devices: GEMINI 
// Tool Versions: --
// Description: 
//            This module reads the sampled data from ocla memory one by one   
//            and send outs to the AXI interface in the AXI_DATA_WIDTH sized word chunks
// Dependencies:  
//   none   
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////



/* verilator lint_off WIDTHCONCAT */
/* verilator lint_off WIDTH */
/* verilator lint_off DECLFILENAME */
`pragma protect begin_protected
`pragma protect author = "Verific"
`pragma protect author_info = "Verific Corporation"
`pragma protect data_method = "aes128-cbc"
`pragma protect key_keyowner = "Verific"
`pragma protect key_keyname = "key1"
`pragma protect key_method = "rsa"
`pragma protect encoding = (enctype = "base64", line_length = 64, bytes = 128), key_block
MNuUStdQ7xmy6gHCLB8x7M1MrbU+KOnHPgGuEsADCsIW7fwelix7b7Aj2WqMUPPn
WGJSsTFU40QFMixzcif0/NE4Iz8UZC29oU3J5HmacMhtmYpJw/eHyjlHwWA14jKd
+T9kCb9sJznAQ5URDw+PrWkYk9Eue+gtWNwjKMzH2N8=
`pragma protect encoding = (enctype = "base64", line_length = 64, bytes = 128), data_block
adZ3bhMjiYoszIl8qAFwDPU0+dap6YU5KMk+iIiUWFku8PgvXpksQhoM4Zv5Crhy
eeRJRMD9HrlFVWOgT78hbED5CICFTU0btHD2H9sDyBoN4PLKYEiIOlDzY5jrUhvH
0xg2kd9iE6UGQke75BRAAilwYX2vrn/LBI2JwhyjGe0lPEnAgj1pnGNgfbe18BFI
5+uF9p2GPckBmmeMnGhxeyGklrQdy00LOn/+jKAT1HJZA6ZKg3MuW41Z1L2Ra40W
WInKZQnTVV7bCHjQ8K2uh8lPyzPXj2U5txa09RO36ooGpgYVKa28F9Mb4eGSRayT
4CZ67F35/fbu6v4pzQeV3sJiFLaLwNr49ZrbBVpFA5mU6iI7HUh4Tyhj6+tiXzhc
K/or4g4cKH/CEowIWMQbQm2+J53pIx17jBhHgCw0bIMue0NASqJjb+mBClh4djlm
CtuG3j/DnfhmVlTrOcXUpRa4eCvEn5LvEu2IAuQAmu0/cGE4lmoN0crY4kiGreOV
w1cEZ0+eqy5SP+O/c/fJmTkF8IOp9GgQtAS9sFDSScRtYIx4vfLTvRvNW9eOkIN3
vO96cFd+W+hxpAi11z8k9oXQLyh1l9tLdBhRWR+UfPcxJXMcuAzD7RcsfHNjEoVb
tIx57/0idv4WgcQJQWB0ORQ7mp5BbqPmhudLxUKjHMxQPx7dxs/1KGF+0bIMEntx
qTGWrMq2x9qKz2DaaVtDTK2EOFEjEk1ENx1SsSkJGBzUHaRbjG6BCh04omzzw/qN
mc8M0/FhnGVvRfNQtHcvIpzfN0qY1jzy9vsoI9AhMebqQKCvhWH3tsgRlz5Xy9S4
envRDo405gJ2r1wSHSZtIo+GvpJ2HFyL++xW8wVPB7lwO4kqhFebkyuZXpj96uv6
OOqZKdFlFJOw4J3ANMqS1rUd+eCq86R/GLpwS4vFwM0Y0MYuWn8SRer9/DP2GPtX
FuUaPpGhTipIlHgBSq+lFZYd1Gw+4//JOxXjLX4ynwSvLgoeJaU2vK/rD3ugkDoa
nDrzoiO1/9z73KYM8FFj94Na9/FV/Ff9Bym+Nbxm0hrB+78/R9FpyNHngtahGriu
nJ/CUVRhbCd0n26gKI1+Fat5kwWj30NB6Xgwq17vCMvb1SDC6DPmOsJW/JMwItzI
eGpQk2Rg3BJKvQzWOUuf1kH7pawBMsdlvAxobHmd7K4Dhn1dqzH9LcdPfBV8kCmr
47nSI7FJAjAfU76aLFcGtkLmcQ0Io7BCrlLtZW5ov5aoRdNf0rkWsRPYpj9EPnQa
aPch+YixCLNa/yuABC4zhDiIqUQU5Z4909yGqoShFUhkhALOz31wkvc4cqZ4O5Ku
7XO/Ie5nrnOHqwPzArr20/MjTmKWuNIPXpx1bSRcgXq+0DVgjQH9T1qTyrzwHLAA
dUBAS4x7lL4GMgKXLmfzZQox5oSG0AH5gDj+qnb21w1ZYiydBz5dV7cciGqSuZZT
FwSwvWGFjhT6lUcQh0XAaT5OYLS7IH1ziYMjvhu9yUlo4o4svJQbqKPlu/vV/1Ub
fGF35MESy+Ce8qye1NF8gRzeJPTYp1etc9clwgFfERc7aIaKQ7YNJmUxIvt3xeV4
KgRovZVuD/lGLeePKkdcXTCyVzbBUmuEkYAa7huGnPbAT5l4HXiFVBOBMRUdN2D4
6UPIG9K1/5PG6dIQ2c/GNEE/qzrVOvSLa6jdWu5qew/8pNUuuCY/WGQVTNKruyes
8M1/36EQhqpgtvfx6hh1ukieE/+BwXGRTgfkHRANC4sIrmJrmTavNwOhdkJMApPs
AuFtVlPZg9b9H/ni73JYEh8Puy01KNNcMxqgeLICOc6WzjjDrd9hfxZ3adWpFy7M
QK25OJlZEN5tJDbvaXIhzilE0kZENm1rBT28Nff/H7qIRgEDcs9ZnhM/DKfhqymC
EyhDynzs+iRVP8jAvRFf4409yzsAc+0yCt8NQ7uBxVMrOvCPH+/q9kaOFeID6E8A
kKuC9aX71T18waF8nZdG0094zgsvrGmHUabf+yIOIIkfdhVNrYKzemMTCLNFLhSR
lMmjd5TZ4slEexvpUhbf9xrEUZcm8E0zv5Mx22yUwR05Vjt2e+HNOMnCiVzcb/8q
qWqzFyq3nej4cwfVu/nqLGpl05bh6Mj6/1EaVqSdRo4DBYuXMV212rAV+8ddXtii
QnotrN4DpucxSZOJrNaq89ALMkh7QbDS1w4GIH5yIL4INJJT1Fa+g7Xul7T1Mv73
l6/XSmCNSQbD524nUpHwprWcWHYFmwcLwbdFJWhYX2I4qGryUGoIlykmv+9kvaiI
c46MJxeGGxHog7UtW3JQoPHkb+7Y27wzjCJCkT1glQwLmmU9b0g/dVOEkXMRCU+h
f1GPQf/s9Dxc6Q9zHY6bVwYJjRfS5LArSiSr/sVq4+ren5G9k7JjvYRDbRisrfkk
mz1dZZsC8fTcX8LvxsZqOCd1rjLVut4eyGf476dgNLZPzDPw41dVZhwM1LhAQfzp
XHPO/ScdW4SsYhKG/BWFI1QqDEk/0FW3irKJvHm4nmtjOl18EOBMVCLyoverNdcN
n1aRI5CP5ULARt4WK1ALMsWVpMTH+Bidmt8kE607LRyMNFyrrxr3TNKZyMltrXMC
RYE2rW+mj4p9qHTXodspJnqgTviK4iwLzF+dxs5bHRJjdS1pFqLSsAeQQTC2LH46
lHDMVMEWy3GzsoDbMZaDqHnpE5wydRLI9rCjms67k4swEtfeV0RCq44a4tRagvSR
G43+1cKa0ZFjCkeVzwQiw89Q53wYxzJlklMcvH74eNJKV9gQYd3mdJb5VjjJ936I
3msi64hVP11Xaam0FpbQ2goCE5KpujmEwsonUhsjDvi62PW51bTN8fWKlj0PkhIi
JlLS7rZy5Z0EpMa7HqL4URHHAqPuejkQmN9urPpb509pPlcehyh3aIDeGi4QrDvG
urut/rGWt0jACXIFz/2sqM8F/gyYxsKtL26LZC4rPNUiLqQH8atTLL3q2/d2nDgX
MHHaZd0ShYHxTHgBcWlumDnMdhHgqkTHmLqU8aRy32K5HginTOO74/f3WZPVk+cv
CX7jnT3YEsSsH0gRktdCTUDQM6iwAHzC91Yz44bekqcNif/lYNy9WnJwflw1dRCY
MVx1esVHQcD82QPu4t+J4T0wJU8EuVbtieimz8F3NwLsYZFXNoFiEyan4754zIFh
2edkvwvybs5YOmP/VJOeScKY4iyCIIyvju+62ohrHEPL8B4jr9BTok+agjbOZSL8
7hV1v0zv/Zx/UdEQVJ2OKsvx0In2Xaqs7anYWXVqDI+LOPV6kmmmrZSDTn9p6C7T
ZW0lQ6x7NIUNrmfxWP7es0y8xFEWe03Z/NXXRzSxey3AS7lb5pKWsYqsgKHifZ5x
w1PV1eyt/YZSknomZNrAnClRnMjICXjHAeR3pv7FhBqaysTlVd0BzaaDJUDoHlug
whWgxdoiyFSq8f/Edkn8AhRe1YPWDVIuKI/CexwQuCHsNKkZDTFqSILygwEljbdM
/dYG8SfxpnlQm48j7l3Ghq5NxbYH3tkhZl6gEnat6lUjfCPvuEhuPxA0ODA8taPk
5shrt3vAv2/RyA9N1N8zQeAEl0KpkDlH6ruvpz0BIRTY0z+KSXcJfg1FZ1YqPrU7
nL0ZN9UYhriEKVclIYm04+hm1f8Ym+/4lNFwqRzvDKP/eQNpc8BKZTIuq+aKHUH9
jeH0yoSxJkTkz2ctt3NnymuycSk5+EBl2vlu4ZBrt172ZpIRtaP9O8ZwSJMb8dsd
F/cyxc7voCNRyI+z+nUKsPA8cdR4N+UaOTqKaCaGpf6qqY0WFZ6yQ3cyzFvX6EpQ
FFcLswdJhkN9pkekuqVmtr6TJuadpxZn+992JI4h8zxeM8k8GAqPOy8FA+r1Vj8Y
JxoSRQ/lvIBmmQ6DlpEn3GSafzepvtEKr2MJ9zCDlKVgMTtrGHlBEC9haJfyJkwu
Kq3g9g3UDnfm+xsfZf1wLamHKnj7RB54EERAxr1cYAafBnJQTwmtzJUgycYbNXzq
F0nY0p4LTVWDyVct4TGzGpQJZpDiYgx1DFz5757CKhhaKjI713f0yolA+u6yvwBs
c22s+gLuM45Dvjj3Gpm8ivaiigYZBM290LMSfy6PMhVrX4FwTbbpR7W8L/2s5pBP
xYhVsSu6aTUuextFN/UDgR9o6j6Bdm4GELDQWeZ40EeSTNafGl0ykYoGxhM9SV+6
iOP1sIZNxamwBXmnxDZQ/sQi8OzJAjl/vo+eCHdg9NRIrtnNYgG3Y1bwz0E3Rw9/
x8VRcYkR05/cylr8PeBiXA7p6Fy1fXTQUeKLDXr8rwkBJOfWpS2BvxoaFoU24tPP
oG7/eceDHqbphp9+dT3lOq01FlUETU+QKNSs+mjM5gxp/S0BVvmpYiprDyn2eP47
6zcRP6VGo8AWNqAZZp+tf697KDpd6tmoSkj+Xw0yndkhq1eKtNz2isrxs3y6iCdF
cCQ9GvOhBR8d+p2nuP/Sx5m3fnCGt0D/ZUf/DyuVbFa1r8DqQTbgqIGgVXX2gfqF
Hldu4N6kjObnciS+6YYfJtkYHChtuvoLkrXOyPEm+XlkUUopEpUA8L644O2apwuD
oeLxVr0qJTSxDSy6estEZoQ3qxqsZ4uoEYHPaKg0z0A8ugtaUZ8z5E4vCMAodLHn
QgnacVxgfvGeU4QdoWA4zROKnDZ6DoqU510t8r0BZ2ohUwtrcprs1VDZfwX3JF72
WZ8nxyHlSewzkLlT2R61uCVpIn/Tf4F8Ddz5iIPN7t+v3XUVm4nXk0CRoJatpNu3
Itj9INiMpU9l04zw2+Df7KWc5F7VxMJYV+us2QYVBQUQl3inAAX7RlDLOBM1Q96d
mjRVsk8SwTs8SE05w0Vi2Gt+7wcl7ChOAUMJ7vnbe4VLe2QTmybLYxuAtHs6CSCh
5QyJxBgg7eocWCakytyOGrzY6cjLi34bNMea+6rXxQ9y9Z6TLNWxr6d/d+ZMwzTJ
ENITx++qd0nBX+WHTzGnLSTIi6dqxukQwQwU1o84DEVe8EHDOFXqrBP5Cik9E6a+
IxLvUzHx16AskcGY8qqM04XIw13VJ/EagZP1Baqib0obH42HS46LrtWpiLQm0iar
ujl2QottEbVMfC+ifombU50+Ocv1BZxLpVpD7QZvDVjV/N0begPZgQuMNZgpGYqI
g0wcwJAXj8XRHb58htwt6cWr4yiMQu/eqsELvOmxD56xDgP0ZjlOaOrPoCNmzI+4
oM2VuUrN7AGuz5x6RvqBO/Hm3kRdkaeZITba1JclUjzO2IgIVPEXGWTgjjDaK/il
sUPQFqeXFUft/X5k/WDkbTpe5EpLkw0sBpvM06rqyikG2tE1hkVTqbPE4KwgTIy0
j9SMCOf+piSmNsaLMLZhKWAHXAq5cDOP8yQ53FT0klUluRml8K6nHF0EiBngdXMH
RMfURjzhdWlNHRbtscQOZFmKxaFw4R8ursSO5TNtwuxJqCwjS8y3QeTcpSJycG35
aQ+4TXIT3/b/rBGfnypz6Ep5L06sseuGwmb6QOgxiNXMLdUpi3odNPqEbl8dmf1q
/j+Lx9r/0HJjGDrp4q3IpOLhikYVXdgDPtTcEof7G9LhJYxgIz2nB6cFfXw4dqXx
8Z6PBug51vcme7PtFO7FKcH9kjz1LX+eCYBRWkOjn9dX3wO/YAae9OElLCJ0l3WF
gLQGzoHeW2FXYo/BWwjGIt6/UdS3FGvdF3ZKYleKGlQ=
`pragma protect end_protected
