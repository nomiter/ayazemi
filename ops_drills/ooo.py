import sys
N = int(input())
bt,bx,by = 0, 0, 0
for line in range(N):
  t,x,y = map(int, input().split(" "))
  a = abs(int(x) -bx) + abs(int(y) -by)
  dt = t-bt
  if int(dt) >= a and a%2 == dt%2:
    bt, bx, by = t, x, y
  else:
    print("No")
    break
else:
  print("Yes")