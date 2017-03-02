import random

random.seed(12345)

unsorted_values = [random.randint(0, 63) for i in xrange(100)]

def sort(array, start, length):
  array[start:start + length] = sorted(array[start:start + length])

sort(unsorted_values, 0, 13)
sort(unsorted_values, 13, 16)
sort(unsorted_values, 29, 30)
unsorted_values[29:59] = list(reversed(unsorted_values[29:59]))
sort(unsorted_values, 59, 41)


figures = []

print """input boxes;
prologues := 2;
verbatimtex
\documentclass{article}
\pagestyle{empty}
%\usepackage{mathpazo}
\\begin{document}
etex

numeric u;
u := 2mm;

vardef fillbox(expr ux, uy, width, height, shade) =
  fill (ux,uy)--(ux+width,uy)--(ux+width,uy-height)--(ux,uy-height)--cycle withpen pensquare scaled 1pt withcolor shade*white;
enddef;

vardef drawbox(expr ux, uy, width, height, r, g, b) =
  draw (ux,uy)--(ux+width,uy)--(ux+width,uy-height)--(ux,uy-height)--cycle withpen pensquare scaled 3pt withcolor (r*red + g*green + b*blue);
enddef;
"""

figno = 1

colors = []
for i in xrange(100):
  red = random.random()
  green = random.random()
  blue = random.random()
  colors.append((red, green, blue))

def make_figure(values, stack=[]):
  global figno
  text = "beginfig(%d);" % figno
  text += "pickup pensquare scaled 1pt;"
  for i, v in enumerate(values):
    text += "fillbox(%d * u, 0, u, 4*u, %f);" % (i, v / 63.0)

  for (start, length), color in zip(stack, colors):
    text += "drawbox(%d * u, 0, %d * u, 4 * u, %f, %f, %f);" % (start, length, color[0], color[1], color[2])

  text += "endfig; %% %d" % figno
  figno += 1
  print text

def compute_minrun(size, max_size=16):
  max_bits = -2
  while max_size != 0:
    max_size >>= 1
    max_bits += 1

  top_bit = 31
  while size & (1 << top_bit) == 0:
    top_bit -= 1
  shift = max(top_bit, max_bits) - max_bits
  minrun = size >> shift
  mask = (1 << shift) - 1
  if mask & size != 0:
    return minrun + 1
  return minrun

minrun = compute_minrun(len(unsorted_values))
stack = []
print "%% minrun = %d"
print "%% stack = %s" % str(stack)

make_figure(unsorted_values)

array = unsorted_values
curr = 0

from collections import namedtuple


def count_run(array, start):
  if start + 1 >= len(array) - 1:
    return len(array) - start
  if array[start] > array[start + 1]:
    for i in xrange(start + 1, len(array) - 1):
      if array[i] < array[i + 1]:
        break
    else:
      i += 1
    # Reverse run
    array[start:i + 1] = list(reversed(array[start:i + 1]))
  else:
    for i in xrange(start + 1, len(array) - 1):
      if array[i] > array[i + 1]:
        break
    else:
      i += 1
  return i - start + 1

def push_next():
  global stack
  global array
  global curr
  length = count_run(array, curr)
  run = minrun
  if run > len(array) - curr:
    run = len(array) - curr
  if run > length:
    sort(array, curr, run)
    length = run
  stack.append((curr, length))
  curr += length
  make_figure(array, stack)
  if curr == len(array):
    while len(stack) > 1:
      merge_right(array, stack)
      make_figure(array, stack)


def check_invariant(stack):
  if len(stack) < 2:
    return True
  if len(stack) == 2:
    a = stack[0][1]
    b = stack[1][1]
    if a <= b:
      return False
    return True
  a = stack[-3][1]
  b = stack[-2][1]
  c = stack[-1][1]
  if (a <= b + c) or (b <= c):
    return False
  return True

def collapse(stack):
  if len(stack) == 2:
    b = stack.pop()
    a = stack.pop()
    sort(array, a[0], a[1] + b[1])
    stack.append((a[0], a[1] + b[1]))
    make_figure(array, stack)
    return
  a = stack[-3][1]
  b = stack[-2][1]
  c = stack[-1][1]
  if a <= b + c:
    if a < c:
      # merge a, b
      merge_left(array, stack)
    else:
      # merge b,c
      merge_right(array, stack)
  else:
    merge_right(array, stack)
  make_figure(array, stack)


def merge_left(array, stack):
  acurr, alen = stack[-3]
  bcurr, blen = stack[-2]
  sort(array, acurr, alen + blen)
  c = stack.pop()
  b = stack.pop()
  a = stack.pop()
  stack.append((acurr, alen + blen))
  stack.append(c)

def merge_right(array, stack):
  acurr, alen = stack[-2]
  bcurr, blen = stack[-1]
  sort(array, acurr, alen + blen)
  b = stack.pop()
  a = stack.pop()
  stack.append((acurr, alen + blen))


print "%% push_next"
push_next()
print "%% stack = %s" % str(stack)
print "%% push_next"
push_next()
print "%% push_next"
push_next()

while stack[0][1] != len(array):
  if not check_invariant(stack):
    collapse(stack)
    continue
  push_next()


footer = """
verbatimtex
\end{document}
etex
bye
"""
print footer