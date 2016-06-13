
import numpy as np
import time

startTime = time.time()

a = np.random.rand(10000,10000)

aInv = np.linalg.inv(a)

endTime = time.time()

print('Total Execution Time : %.3f' % (endTime-startTime))
