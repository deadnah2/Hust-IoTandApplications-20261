#ifndef LED_MANAGER_H
#define LED_MANAGER_H

class LedManager {
public:
    LedManager(int pin);
    void begin();
    void on();
    void off();
    void toggle();
    bool getState();

private:
    int _pin;
    bool _state;
};

#endif // LED_MANAGER_H
