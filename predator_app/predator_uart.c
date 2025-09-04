#include "predator_uart.h"
#include <furi_hal_uart.h>
#include <furi_hal_resources.h>

#define PREDATOR_UART_RX_BUF_SIZE 2048

struct PredatorUart {
    FuriHalUartId uart_id;
    FuriThread* rx_thread;
    FuriStreamBuffer* rx_stream;
    PredatorUartRxCallback rx_callback;
    void* rx_callback_context;
    bool running;
};

static int32_t predator_uart_rx_thread(void* context) {
    PredatorUart* uart = (PredatorUart*)context;
    uint8_t data[64];
    
    while(uart->running) {
        size_t len = furi_stream_buffer_receive(uart->rx_stream, data, sizeof(data), 100);
        if(len > 0 && uart->rx_callback) {
            uart->rx_callback(data, len, uart->rx_callback_context);
        }
    }
    
    return 0;
}

static void predator_uart_on_irq_cb(UartIrqEvent ev, uint8_t data, void* context) {
    PredatorUart* uart = (PredatorUart*)context;
    
    if(ev == UartIrqEventRXNE) {
        furi_stream_buffer_send(uart->rx_stream, &data, 1, 0);
    }
}

PredatorUart* predator_uart_init(
    const GpioPin* tx_pin,
    const GpioPin* rx_pin,
    uint32_t baud_rate,
    PredatorUartRxCallback rx_callback,
    void* context) {
    
    PredatorUart* uart = malloc(sizeof(PredatorUart));
    
    // Determine UART ID based on pins
    if(tx_pin == &gpio_ext_pc0 && rx_pin == &gpio_ext_pc1) {
        uart->uart_id = FuriHalUartIdUSART1;
    } else if(tx_pin == &gpio_ext_pb2 && rx_pin == &gpio_ext_pb3) {
        uart->uart_id = FuriHalUartIdLPUART1;
    } else {
        uart->uart_id = FuriHalUartIdUSART1; // Default
    }
    
    uart->rx_callback = rx_callback;
    uart->rx_callback_context = context;
    uart->running = true;
    
    uart->rx_stream = furi_stream_buffer_alloc(PREDATOR_UART_RX_BUF_SIZE, 1);
    
    furi_hal_uart_init(uart->uart_id, baud_rate);
    furi_hal_uart_set_irq_cb(uart->uart_id, predator_uart_on_irq_cb, uart);
    
    uart->rx_thread = furi_thread_alloc_ex("PredatorUartRx", 1024, predator_uart_rx_thread, uart);
    furi_thread_start(uart->rx_thread);
    
    return uart;
}

void predator_uart_free(PredatorUart* uart) {
    furi_assert(uart);
    
    uart->running = false;
    furi_thread_join(uart->rx_thread);
    furi_thread_free(uart->rx_thread);
    
    furi_hal_uart_deinit(uart->uart_id);
    furi_stream_buffer_free(uart->rx_stream);
    
    free(uart);
}

void predator_uart_tx(PredatorUart* uart, uint8_t* data, size_t len) {
    furi_assert(uart);
    furi_hal_uart_tx(uart->uart_id, data, len);
}

void predator_uart_set_br(PredatorUart* uart, uint32_t baud) {
    furi_assert(uart);
    furi_hal_uart_set_br(uart->uart_id, baud);
}
