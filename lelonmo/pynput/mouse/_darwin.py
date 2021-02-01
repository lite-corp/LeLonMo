# coding=utf-8
# pynput
# Copyright (C) 2015-2020 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
The mouse implementation for *macOS*.
"""

# pylint: disable=C0111
# The documentation is extracted from the base classes

# pylint: disable=R0903
# We implement stubs

import enum
import quartz

from AppKit import NSEvent

from lelonmo.pynput._util.darwin import (
    ListenerMixin)
from . import _base


def _button_value(base_name, mouse_button):
    """Generates the value tuple for a :class:`Button` value.

    :param str base_name: The base name for the button. This should be a string
        like ``'kCGEventLeftMouse'``.

    :param int mouse_button: The mouse button ID.

    :return: a value tuple
    """
    return (
        tuple(
            getattr(quartz, '%sMouse%s' % (base_name, name))
            for name in ('Down', 'Up', 'Dragged')),
        mouse_button)


class Button(enum.Enum):
    """The various buttons.
    """
    unknown = None
    left = _button_value('kCGEventLeft', 0)
    middle = _button_value('kCGEventOther', 2)
    right = _button_value('kCGEventRight', 1)


class Controller(_base.Controller):
    #: The scroll speed
    _SCROLL_SPEED = 5

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self._click = None
        self._drag_button = None

    def _position_get(self):
        pos = NSEvent.mouseLocation()

        return pos.x, quartz.CGDisplayPixelsHigh(0) - pos.y

    def _position_set(self, pos):
        try:
            (_, _, mouse_type), mouse_button = self._drag_button.value
        except AttributeError:
            mouse_type = quartz.kCGEventMouseMoved
            mouse_button = 0

        quartz.CGEventPost(
            quartz.kCGHIDEventTap,
            quartz.CGEventCreateMouseEvent(
                None,
                mouse_type,
                pos,
                mouse_button))

    def _scroll(self, dx, dy):
        dx = int(dx)
        dy = int(dy)
        while dx != 0 or dy != 0:
            xval = 1 if dx > 0 else -1 if dx < 0 else 0
            dx -= xval
            yval = 1 if dy > 0 else -1 if dy < 0 else 0
            dy -= yval

            quartz.CGEventPost(
                quartz.kCGHIDEventTap,
                quartz.CGEventCreateScrollWheelEvent(
                    None,
                    quartz.kCGScrollEventUnitPixel,
                    2,
                    yval * self._SCROLL_SPEED,
                    xval * self._SCROLL_SPEED))

    def _press(self, button):
        (press, _, _), mouse_button = button.value
        event = quartz.CGEventCreateMouseEvent(
            None,
            press,
            self.position,
            mouse_button)

        # If we are performing a click, we need to set this state flag
        if self._click is not None:
            self._click += 1
            quartz.CGEventSetIntegerValueField(
                event,
                quartz.kCGMouseEventClickState,
                self._click)

        quartz.CGEventPost(quartz.kCGHIDEventTap, event)

        # Store the button to enable dragging
        self._drag_button = button

    def _release(self, button):
        (_, release, _), mouse_button = button.value
        event = quartz.CGEventCreateMouseEvent(
            None,
            release,
            self.position,
            mouse_button)

        # If we are performing a click, we need to set this state flag
        if self._click is not None:
            quartz.CGEventSetIntegerValueField(
                event,
                quartz.kCGMouseEventClickState,
                self._click)

        quartz.CGEventPost(quartz.kCGHIDEventTap, event)

        if button == self._drag_button:
            self._drag_button = None

    def __enter__(self):
        self._click = 0
        return self

    def __exit__(self, exc_type, value, traceback):
        self._click = None


class Listener(ListenerMixin, _base.Listener):
    #: The events that we listen to
    _EVENTS = (
        quartz.CGEventMaskBit(quartz.kCGEventMouseMoved) |
        quartz.CGEventMaskBit(quartz.kCGEventLeftMouseDown) |
        quartz.CGEventMaskBit(quartz.kCGEventLeftMouseUp) |
        quartz.CGEventMaskBit(quartz.kCGEventLeftMouseDragged) |
        quartz.CGEventMaskBit(quartz.kCGEventRightMouseDown) |
        quartz.CGEventMaskBit(quartz.kCGEventRightMouseUp) |
        quartz.CGEventMaskBit(quartz.kCGEventRightMouseDragged) |
        quartz.CGEventMaskBit(quartz.kCGEventOtherMouseDown) |
        quartz.CGEventMaskBit(quartz.kCGEventOtherMouseUp) |
        quartz.CGEventMaskBit(quartz.kCGEventOtherMouseDragged) |
        quartz.CGEventMaskBit(quartz.kCGEventScrollWheel))

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self._intercept = self._options.get(
            'intercept',
            None)

    def _handle(self, _proxy, event_type, event, _refcon):
        """The callback registered with *macOS* for mouse events.

        This method will call the callbacks registered on initialisation.
        """
        try:
            (px, py) = quartz.CGEventGetLocation(event)
        except AttributeError:
            # This happens during teardown of the virtual machine
            return

        # Quickly detect the most common event type
        if event_type == quartz.kCGEventMouseMoved:
            self.on_move(px, py)

        elif event_type == quartz.kCGEventScrollWheel:
            dx = quartz.CGEventGetIntegerValueField(
                event,
                quartz.kCGScrollWheelEventDeltaAxis2)
            dy = quartz.CGEventGetIntegerValueField(
                event,
                quartz.kCGScrollWheelEventDeltaAxis1)
            self.on_scroll(px, py, dx, dy)

        else:
            for button in Button:
                try:
                    (press, release, drag), _ = button.value
                except TypeError:
                    # Button.unknown cannot be enumerated
                    continue

                # Press and release generate click events, and drag
                # generates move events
                if event_type in (press, release):
                    self.on_click(px, py, button, event_type == press)
                elif event_type == drag:
                    self.on_move(px, py)
