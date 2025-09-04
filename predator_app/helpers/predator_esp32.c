#include "../predator_i.h"
#include <furi_hal_gpio.h>
#include <furi_hal_serial.h>
#include <furi_hal_bus.h>

#define ESP32_UART_BAUD PREDATOR_ESP32_UART_BAUD
#define ESP32_BUFFER_SIZE 256

static void predator_esp32_rx_callback(uint8_t* data, size_t size, void* context) {
    PredatorApp* app = context;
    if(app->esp32_stream) {
        furi_stream_buffer_send(app->esp32_stream, data, size, 0);
    }
}

void predator_esp32_init(PredatorApp* app) {
    // Initialize UART for ESP32 communication
    // Check Marauder switch state before initializing
    furi_hal_gpio_init(PREDATOR_MARAUDER_SWITCH, GpioModeInput, GpioPullUp, GpioSpeedLow);
    if(!furi_hal_gpio_read(PREDATOR_MARAUDER_SWITCH)) {
        app->esp32_connected = false;
        return; // Marauder switch is off
    }
    
    furi_hal_gpio_init(PREDATOR_ESP32_UART_TX_PIN, GpioModeAltFunctionPushPull, GpioPullNo, GpioSpeedVeryHigh);
    furi_hal_gpio_init(PREDATOR_ESP32_UART_RX_PIN, GpioModeAltFunctionPushPull, GpioPullNo, GpioSpeedVeryHigh);
    
    app->esp32_uart = predator_uart_init(PREDATOR_ESP32_UART_TX_PIN, PREDATOR_ESP32_UART_RX_PIN, ESP32_UART_BAUD);
    app->esp32_stream = furi_stream_buffer_alloc(ESP32_BUFFER_SIZE, 1);
    app->esp32_connected = false;
    
    // Send Marauder status command
    predator_esp32_send_command(app, MARAUDER_CMD_STATUS);
}

void predator_esp32_deinit(PredatorApp* app) {
    if(app->esp32_stream) {
        furi_stream_buffer_free(app->esp32_stream);
        app->esp32_stream = NULL;
    }
    
    predator_uart_deinit(app->esp32_uart);
    app->esp32_connected = false;
}

bool predator_esp32_send_command(PredatorApp* app, const char* command) {
    if(!app || !app->esp32_uart || !command) return false;
    
    size_t len = strlen(command);
    predator_uart_tx(app->esp32_uart, (uint8_t*)command, len);
    predator_uart_tx(app->esp32_uart, (uint8_t*)"\r\n", 2);
    
    return true;
    
    return false;
}

bool predator_esp32_is_connected(PredatorApp* app) {
    return app->esp32_connected;
}
