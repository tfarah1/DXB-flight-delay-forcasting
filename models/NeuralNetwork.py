from tensorflow import keras
from matplotlib import pyplot as plt
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.models import load_model


class NeuralNetwork():
    def __init__(self, X_train, X_test, y_train, y_test, model_weights_PATH):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.model_weights_PATH = model_weights_PATH

    @staticmethod
    def create_model(layer_sizes, input_shape, activation_functions, output_layer_size):
        num_layers = len(layer_sizes)
        model = keras.Sequential()
        model.add(keras.layers.Dense(
            layer_sizes[0], activation=activation_functions[0], input_shape=input_shape))
        for i in range(1, num_layers):
            model.add(keras.layers.Dense(
                layer_sizes[i], activation=activation_functions[i]))
        model.add(keras.layers.Dense(output_layer_size))
        print(model.summary())
        return model

    def run_model(self, model, epochs, batch_size=32, lr=0.001, loss='mean_squared_error', early_stopping_bool=True, monitor='val_loss', patience=10, restore_best_weights=True, model_checkpoint_bool=True, save_best_weights_only=True):
        optimizer = Adam(learning_rate=lr)
        model.compile(optimizer=optimizer, loss=loss)
        callbacks = []
        if early_stopping_bool:
            early_stopping = EarlyStopping(
                monitor=monitor,
                patience=patience,
                restore_best_weights=restore_best_weights)
            callbacks.append(early_stopping)
        if model_checkpoint_bool:
            model_checkpoint = ModelCheckpoint(
                self.model_weights_PATH, save_best_only=save_best_weights_only)
            callbacks.append(model_checkpoint)
        history = model.fit(
            self.X_train, self.y_train,
            epochs=epochs,
            batch_size=batch_size,
            verbose=1,
            validation_data=(self.X_test, self.y_test),
            callbacks=callbacks
        )
        return history

    @staticmethod
    def plot_losses(history):
        loss = history.history['loss']
        val_loss = history.history['val_loss']
        epochs = range(1, len(loss) + 1)
        plt.figure(figsize=(10, 5))
        plt.plot(epochs, loss, label='Training Loss')
        plt.plot(epochs, val_loss, label='Validation Loss')
        plt.title('Training and Validation Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.show()

    def predict(self):
        model = load_model(self.model_weights_PATH)
        y_pred = model.predict(self.X_test)
        return y_pred
