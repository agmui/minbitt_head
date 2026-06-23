#include <hardware/uart.h>
#include <hardware/gpio.h>

#define NUM_BUTTONS 8

// sets bit in BYTE at index N to X
#define SET_BIT(BYTE, N, X) (((uint8_t)X << N) | BYTE & ~((uint8_t)1 << N))

const int button_to_pin[NUM_BUTTONS] = {28,27,26,21,20,19,17,18}; // maps button index to pin number
bool last_button_state[NUM_BUTTONS] = {LOW, LOW, LOW, LOW, LOW, LOW, LOW};
uint8_t button_state = 0x0;

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long last_debounce_time[NUM_BUTTONS] = {0};  // the last time the output pin was toggled
const unsigned long debounceDelay = 10;    // the debounce time; increase if the output flickers

// debounce taken from: https://docs.arduino.cc/built-in-examples/digital/Debounce/
void debounce(uint8_t pin, uint8_t reading){
  if (reading != last_button_state[pin])                       // If the switch changed, due to noise or pressing:
    last_debounce_time[pin] = millis();                        // reset the debouncing timer

  if ((millis() - last_debounce_time[pin]) > debounceDelay)    // whatever the reading is at, it's been there for longer than the debounce delay, take it as the actual current state:
        button_state = SET_BIT(button_state, pin, reading);    // sets bit to reading at given pin index

  last_button_state[pin] = reading;
}

void setup() {
  Serial.begin(115200);

  uart_init(uart0,115200);                         // UART_USB and UART0 are diffrent so we can use both at the same time https://github.com/orgs/micropython/discussions/11080
  uart_set_format(uart0, 8, 2, UART_PARITY_EVEN);  // 8 data bits, 2 stop bits, even parity
  gpio_set_function(12, GPIO_FUNC_UART);           // only nice way to specify diffrent pins on arduino IDE https://community.platformio.org/t/change-pi-pico-serial-pins/28004/7

  pinMode(LED_BUILTIN, OUTPUT); // init builtin led

  for (int i=0; i<NUM_BUTTONS; i++) {
    pinMode(button_to_pin[i], INPUT_PULLUP);           // Set the button pin as input with an internal pull-up resistor
  }
}

void loop() {
  for (uint8_t i=0; i<NUM_BUTTONS; i++) {
    uint8_t reading = !digitalRead(button_to_pin[i]);  // Note: It's inverted because of pulup resistor
    debounce(i, reading);
  }
  Serial.println(button_state);

  uart_putc_raw(uart0, button_state);

  digitalWrite(LED_BUILTIN, button_state); // blink led when any btn is presssed

  delay(20);  // small delay to avoid reading the button too frequently
}
