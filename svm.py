from sklearn import svm

class SVMClassifier:

	def __init__(self, kernel):
		self.kernel = kernel

	def train(self, samples, labels):
		self.clf = svm.SVC(C=1.0, kernel=self.kernel, degree=3, gamma='auto', coef0=0.0, shrinking=True, probability=False, tol=0.001, cache_size=200, class_weight='balanced', verbose=False, max_iter=-1, decision_function_shape=None, random_state=None)
		self.clf = self.clf.fit(samples, labels)
	
	def classifyAll(self, samples):
		return self.clf.predict(samples)
	
	def toDotFile(self):
		print("unsupported")

class NuSVMClassifier:
	def train(self, samples, labels):
		self.clf = svm.NuSVC()
		self.clf = self.clf.fit(samples, labels)
	
	def classifyAll(self, samples):
		return self.clf.predict(samples)
	
	def toDotFile(self):
		print("unsupported")

class LinearSVMClassifier:
	def train(self, samples, labels):
		self.clf = svm.LinearSVC()
		self.clf = self.clf.fit(samples, labels)
	
	def classifyAll(self, samples):
		return self.clf.predict(samples)
	
	def toDotFile(self):
		print("unsupported")
