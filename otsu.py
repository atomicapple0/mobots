import numpy as np

def otsu(image):
  hist = np.histogram(image.flatten(), range(0,257))
  total = image.size
  current_max, threshold = 0, 0
  sumT, sumF, sumB = 0, 0, 0
  for i in range(0,256):
    sumT += i * hist[0][i]
  weightB, weightF = 0, 0
  varBetween, meanB, meanF = 0, 0, 0
  for i in range(0,256):
    weightB += hist[0][i]
    weightF = total - weightB
    if weightF == 0:
      break
    sumB += i*hist[0][i]
    sumF = sumT - sumB
    meanB = sumB/weightB
    meanF = sumF/weightF
    varBetween = weightB * weightF
    varBetween *= (meanB-meanF)*(meanB-meanF)
    if varBetween > current_max:
      current_max = varBetween
      threshold = i 
  return threshold