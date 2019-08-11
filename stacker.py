#!/usr/bin/env python3
"""
Stacker Clone. 

Max7219  RPi
============
Vcc -> Pin 2
Gnd -> Pin 6
Din -> Pin 19
Cs  -> Pin 24
Clk -> Pin 23
"""
import time

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import show_message
from luma.core.legacy.font import proportional, LCD_FONT, TINY_FONT
from luma.led_matrix.device import max7219
from curtsies import Input
from threading import Thread


class Line(object):
    def __init__(self, x_start, y_pos, direction='right', length=4):
        self._x = x_start
        self._y = y_pos

        self._direction = direction
        self._length = length - 1

    def __str__(self):
        return 'x:' + str(self._x) + ', y:' + str(self._y) + ', length:' + str(self._length)


    def stop(self):
        self._direction = 'stop'


    def update(self, draw):
        if self._direction == 'right':
            self._x += 1
            if self._x + self._length == 8:
                self._direction = 'left'

        elif self._direction == 'left':
            self._x -= 1
            if self._x == -1:
                self._direction = 'right'

        draw.line(
            [(self._x, self._y), (self._x + self._length, self._y)], 
            fill="white"
        )


class StackerGame(object):
    def __init__(self):
        serial = spi(port=0, device=0, gpio=noop())
        self._device = max7219(serial)
        self._state = 'play'
        self._interval = 0.1
        self._lines = []


    def _handle_input(self):
        print('Start thread')
        with Input() as inputs:
            for i in inputs:
                if i == '<SPACE>':
                    self._next_line()
                    time.sleep(0.25)

                if self._state != 'play':
                    break

        print('Stopped thread')


    def _next_line(self):
        last_line = self._lines[-1]
        last_line.stop()

        new_length = 0
        prev_line = None

        if len(self._lines) > 1:
            prev_line = self._lines[-2]
        else:
            prev_line = last_line

        print('Computing new line')
        print(last_line)
        print(prev_line)

        # Compute the new length of the next line
        x1 = max(0, max(last_line._x, prev_line._x))
        x2 = min(7, min(last_line._x + last_line._length, prev_line._x + prev_line._length))
        new_length = max(0, x2 - x1)

        # Handle Game over/Win
        if x2 < x1:
            self._state = 'game_over'
            return
        elif len(self._lines) == 8:
            self._state = 'win'
            return

        # Remove unaligned dots from last line
        last_line._x = x1
        last_line._length = new_length

        print(new_length)

        # Prepare for next line
        self._lines.append(
            Line(-1, last_line._y - 1, length=new_length + 1)
        )
        self._interval *= 0.85


    def _display_msg(self, msg):
        show_message(
            self._device, 
            msg, 
            font=proportional(TINY_FONT),
            fill='white',
            scroll_delay=0.05
        )


    def run(self):
        virtual = viewport(self._device, width=8, height=8)

        # Intro
        self._display_msg('RPi Stacker')

        # Play
        self._input_thread = Thread(target=self._handle_input)
        self._input_thread.start()
        self._lines.append(Line(-1, 7, length=4))

        while self._state == 'play':
            with canvas(virtual) as draw:
                for line in self._lines:
                    line.update(draw)

            time.sleep(self._interval)

        if self._state == 'game_over':
            self._display_msg('Game Over')
        elif self._state == 'win':
            self._display_msg('You win')


if __name__ == '__main__':
    try:
        StackerGame().run()
    except KeyboardInterrupt:
        print('Thank you for playing!')
