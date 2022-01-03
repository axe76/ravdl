import ravop.core.c as R
import numpy as np
import time

class NeuralNetwork():

    def __init__(self, optimizer, loss):
        self.optimizer = optimizer
        self.layers = []
        self.errors = {"training": [], "validation": []}
        self.loss_function = loss()

    def set_trainable(self, trainable):
        for layer in self.layers:
            layer.trainable = trainable

    def add(self, layer):
        if self.layers:
            layer.set_input_shape(shape=self.layers[-1].output_shape())
        if hasattr(layer, 'initialize'):
            layer.initialize(optimizer=self.optimizer)

        # Add layer to the network
        self.layers.append(layer)

    def train_on_batch(self, X, y):
        y_pred = self._forward_pass(X)
        #print("ypred:",y(),y_pred())


        loss = R.mean(self.loss_function.loss(y, y_pred))
        loss.wait_till_computed()
        acc = self.loss_function.acc(y, y_pred)
        loss_grad = self.loss_function.gradient(y, y_pred)
        loss_grad.wait_till_computed()
        #print(loss_grad())
        # Backpropagate. Update weights
        self._backward_pass(loss_grad=loss_grad)
        loss.wait_till_computed()
        return loss(), acc

    def fit(self, X, y, n_epochs, batch_size):
        X = R.Tensor(X)
        y = R.Tensor(y)
        X.wait_till_computed()
        n_samples = len(X())
        for _ in range(n_epochs):
            print("\n\n\nno. of epoch :",_)
            batch_error = []
            for batch in range(0, n_samples, batch_size):
                begin, end = batch, min(batch + batch_size, n_samples)
                batch_y=y.slice(begin=begin, size=end - begin)
                batch_x= X.slice(begin=begin, size=end - begin)
                batch_x.wait_till_computed()
                batch_y.wait_till_computed()
                loss, _ = self.train_on_batch(batch_x, batch_y)
                batch_error.append(float(loss))
            print(batch_error,_)
            self.errors["training"].append(R.mean(R.Tensor(batch_error)))
        return self.errors["training"]

    def _forward_pass(self, X, training=True):
        layer_output = X
        for layer in self.layers:
            layer_output = layer.forward_pass(layer_output, training)
        return layer_output

    def _backward_pass(self, loss_grad):
        for layer in reversed(self.layers):
            loss_grad = layer.backward_pass(loss_grad)

    def predict(self, X):
        X=R.Tensor(X)
        pred= self._forward_pass(X, training=False)
        pred.wait_till_computed()
        print(pred)
        return pred()
