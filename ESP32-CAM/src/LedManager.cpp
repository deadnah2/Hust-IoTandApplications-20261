#include "LedManager.h"
#include "Arduino.h"

LedManager::LedManager(int pin) : _pin(pin), _state(false) {
}

void LedManager::begin() {
    pinMode(_pin, OUTPUT);
    digitalWrite(_pin, LOW);
}

void LedManager::on() {
    digitalWrite(_pin, HIGH);
    _state = true;
}

void LedManager::off() {
    digitalWrite(_pin, LOW);
    _state = false;
}

void LedManager::toggle() {
    _state = !_state;
    digitalWrite(_pin, _state ? HIGH : LOW);
}
