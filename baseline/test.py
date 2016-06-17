
import numpy as np
import time

startTime = time.time()

a = np.random.rand(1000,1000)

aInv = np.linalg.inv(a)

endTime = time.time()

print('Total Execution Time : %.3f' % (endTime-startTime))
