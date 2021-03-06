"""
Keyboard input.

This module contains a class implementing pygame keyboard input.

"""

__author__ = 'Florian Krause <florian@expyriment.org>, \
Oliver Lindemann <oliver@expyriment.org>'
__version__ = ''
__revision__ = ''
__date__ = ''


import time, sys

import pygame

try:
    import android.show_keyboard as android_show_keyboard
    import android.hide_keyboard as android_hide_keyboard
except ImportError:
    android_show_keyboard = android_hide_keyboard = None

import defaults
import expyriment
from expyriment.misc._timer import get_time
from expyriment.misc import unicode2str
from  _input_output import Input

quit_key = None
pause_key = None
refresh_key = None
end_function = None
pause_function = None

class Keyboard(Input):
    """A class implementing a keyboard input.

    Calling `expyriment.control.intialize(exp)` will automatically create a
    keyboard instance and will reference it in exp.keyboard for easy access.

    """

    @staticmethod
    def process_control_keys(key_event=None):
        """Check if quit_key or pause_key has been pressed.

        Reads pygame event cue if no key_event is specified.

        Parameters
        ----------
        key_event : int, optional
            key event to check. If not defined, the Pygame event queue will be
            checked for key down events.

        Returns
        -------
        out : bool
            True if quitting or pause screen has been displayed,
            False otherwise

        """

        if key_event:
            if key_event.type == pygame.KEYDOWN:
                if key_event.key == quit_key and \
                   end_function is not None:
                    confirm = end_function(confirmation=True)
                    if confirm:
                        sys.exit()
                    return True
                elif key_event.key == pause_key and \
                        pause_function is not None:
                    pause_function()
                    return True
                elif key_event.key == refresh_key:
                    if expyriment._active_exp is not None:
                        expyriment._active_exp.screen.update() # todo: How often? double/triple buffering?
        else:
            for event in pygame.event.get(pygame.KEYDOWN):
                # recursion
                return Keyboard.process_control_keys(event)

        return False


    def __init__(self, default_keys=None):
        """Create a keyboard input.

        Parameters
        ----------
        default_keys : int or list, optional
            a default key or list of default keys

        """

        if default_keys is not None:
            self._default_keys = default_keys
        else:
            self._default_keys = defaults.keyboard_default_keys
        Input.__init__(self)

    @property
    def default_keys(self):
        """Getter for default keys"""

        return self._default_keys

    @default_keys.setter
    def default_keys(self, value):
        """Setter for default keys"""

        self._default_keys = value

    @staticmethod
    def get_quit_key():
        """Returns the currently defined quit key """

        return quit_key

    @staticmethod
    def get_pause_key():
        """Returns the currently defined pause key"""

        return pause_key

    @staticmethod
    def set_quit_key(value):
        """Set the currently defined quit key"""

        global quit_key
        quit_key = value

    @staticmethod
    def set_pause_key(value):
        """Set the currently defined pause key"""

        global pause_key
        pause_key = value

    def clear(self):
        """Clear the event queue from keyboard events."""

        pygame.event.clear(pygame.KEYDOWN)
        pygame.event.clear(pygame.KEYUP)

        if self._logging:
            expyriment._active_exp._event_file_log("Keyboard,cleared", 2)

    def read_out_buffered_keys(self):
        """Reads out all keydown events and clears queue."""

        pygame.event.pump()
        pygame.event.clear(pygame.KEYUP)
        rtn = []
        for event in pygame.event.get(pygame.KEYDOWN):
            Keyboard.process_control_keys(event)
            rtn.append(event.key)
        return rtn


    def check(self, keys=None, check_for_control_keys=True):
        """Check if keypress is in event queue.

        Parameters
        ----------
        keys : int or list, optional
            a specific key or list of keys to check
        check_for_control_keys : bool, optional
            checks if control key has been pressed (default=True)

        Returns
        -------
        key : int
            pressed key or None. Only the first occurence is returned!

        """

        if keys is None:
            keys = self.default_keys
        else:
            try:
                keys = list(keys)
            except:
                keys = [keys]
        pygame.event.pump()
        pygame.event.clear(pygame.KEYUP)
        for event in pygame.event.get(pygame.KEYDOWN):
            if check_for_control_keys:
                Keyboard.process_control_keys(event)
            if keys:
                if event.key in keys:
                    if self._logging:
                        expyriment._active_exp._event_file_log(
                            "Keyboard,received,{0},check".format(event.key))
                    return event.key
            else:
                if self._logging:
                    expyriment._active_exp._event_file_log(
                        "Keyboard,received,{0},check".format(event.key), 2)
                return event.key
        return None

    def wait(self, keys=None, duration=None, wait_for_keyup=False,
             check_for_control_keys=True):
        """Wait for keypress(es) (optionally for a certain amount of time).

        This function will wait for a keypress and returns the found key as
        well as the reaction time.
        (This function clears the event queue!)

        Parameters
        ----------
        keys : int or list, optional
            a specific key or list of keys to wait for
        duration : int, optional
            maximal time to wait in ms
        wait_for_keyup : bool, optional
            if True it waits for key-up
        check_for_control_keys : bool, optional
            checks if control key has been pressed (default=True)

        Returns
        -------
        found : char
            pressed character
        rt : int
            reaction time in ms

        Notes
        -----
        Keys are defined my keyboard constants (please use see misc.constants)

        See Also
        --------
        design.experiment.register_wait_callback_function

        """

        if expyriment.control.defaults._skip_wait_functions:
            return None, None
        if android_show_keyboard is not None:
            android_show_keyboard()
        start = get_time()
        rt = None
        found_key = None
        self.clear()
        if keys is None:
            keys = self.default_keys
        else:
            try:
                keys = list(keys)
            except:
                keys = [keys]
        if wait_for_keyup:
            target_event = pygame.KEYUP
        else:
            target_event = pygame.KEYDOWN
        pygame.event.pump()
        done = False
        while not done:
            rtn_callback = expyriment._active_exp._execute_wait_callback()
            if isinstance(rtn_callback, expyriment.control.CallbackQuitEvent):
                done = True
                found_key = rtn_callback
                rt = int((get_time() - start) * 1000)
            for event in pygame.event.get([pygame.KEYDOWN, pygame.KEYUP]):
                if check_for_control_keys and Keyboard.process_control_keys(event):
                    done = True
                elif event.type == target_event:
                    if keys is not None:
                        if event.key in keys:
                            rt = int((get_time() - start) * 1000)
                            found_key = event.key
                            done = True
                    else:
                        rt = int((get_time() - start) * 1000)
                        found_key = event.key
                        done = True
            if duration and not done:
                done = int((get_time() - start) * 1000) >= duration
            time.sleep(0.0005)
        if self._logging:
            expyriment._active_exp._event_file_log("Keyboard,received,{0},wait"\
                                              .format(found_key))
        if android_hide_keyboard is not None:
            android_hide_keyboard()
        return found_key, rt

    def wait_char(self, char, duration=None, check_for_control_keys=True):
        """Wait for character(s) (optionally for a certain amount of time).

        This function will wait for one or more characters and returns the
        found character as well as the reaction time.
        (This function clears the event queue!)

        Parameters
        ----------
        char : int or list
            a specific character or list of characters to wait for
        duration : int, optional
            maximal time to wait in ms
        check_for_control_keys : bool, optional
            checks if control key has been pressed (default=True)

        Returns
        -------
        found : char
            pressed charater
        rt : int
            reaction time in ms

        See Also
        --------
        design.experiment.register_wait_callback_function

        """

        if expyriment.control.defaults._skip_wait_functions:
            return None, None
        start = get_time()
        rt = None
        found_char = None
        self.clear()
        try:
            char = list(char)
        except:
            char = [char]
        pygame.event.pump()
        done = False

        while not done:
            rtn_callback = expyriment._active_exp._execute_wait_callback()
            if isinstance(rtn_callback, expyriment.control.CallbackQuitEvent):
                    done = True
                    rt = int((get_time() - start) * 1000)
                    found_char = rtn_callback

            for event in pygame.event.get([pygame.KEYUP, pygame.KEYDOWN]):
                if check_for_control_keys and Keyboard.process_control_keys(event):
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if event.unicode in char:
                        rt = int((get_time() - start) * 1000)
                        found_char = event.unicode
                        done = True
            if duration and not done:
                done = int((get_time() - start) * 1000) >= duration
            time.sleep(0.0005)
        if self._logging:
            expyriment._active_exp._event_file_log(
                        "Keyboard,received,{0},wait_char".format(
                        unicode2str(found_char)))
        return found_char, rt
