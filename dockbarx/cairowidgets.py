#!/usr/bin/python

#   cairowidgets.py
#
#	Copyright 2009, 2010 Matias Sars
#
#	DockbarX is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	DockbarX is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with dockbar.  If not, see <http://www.gnu.org/licenses/>.

import pygtk
pygtk.require("2.0")
import gtk
import cairo
from math import pi
from common import Globals
from xml.sax.saxutils import escape
import gobject
from pango import ELLIPSIZE_END

from common import connect, disconnect

class CairoButton(gtk.Button):
    """CairoButton is a gtk button with a cairo surface painted over it."""
    __gsignals__ = {"expose-event" : "override",}
    def __init__(self, surface=None):
        gtk.Button.__init__(self)
        self.globals = Globals()
        self.surface = surface

    def update(self, surface):
        a = self.get_allocation()
        self.surface = surface
        if self.window is None:
            # TODO: Find out why is window is None sometimes?
            return
        self.window.clear_area(a.x, a.y, a.width, a.height)
        ctx = self.window.cairo_create()
        ctx.rectangle(a.x, a.y, a.width, a.height)
        ctx.clip()
        ctx.set_source_surface(self.surface, a.x, a.y)
        ctx.paint()

    def do_expose_event(self, event):
        if self.surface is not None:
            ctx = self.window.cairo_create()
            ctx.rectangle(event.area.x, event.area.y,
                           event.area.width, event.area.height)
            ctx.clip()
            a = self.get_allocation()
            ctx.set_source_surface(self.surface, a.x, a.y)
            ctx.paint()
        return

    def cleanup(self):
        del self.surface

    def pointer_is_inside(self):
        b_m_x,b_m_y = self.get_pointer()
        b_r = self.get_allocation()

        if b_m_x >= 0 and b_m_x < b_r.width and \
           b_m_y >= 0 and b_m_y < b_r.height:
            return True
        else:
            return False

class CairoSmallButton(gtk.Button):
    __gsignals__ = {"expose-event": "override",
                    "enter-notify-event": "override",
                    "leave-notify-event": "override",
                    "button-press-event": "override",
                    "button-release-event": "override",}
    def __init__(self, size):
        gtk.Button.__init__(self)
        self.set_size_request(size, size)
        self.mousedown = False
        self.mouseover = False

    def do_enter_notify_event(self, *args):
        self.mouseover = True
        gtk.Button.do_enter_notify_event(self, *args)

    def do_leave_notify_event(self, *args):
        self.mouseover = False
        gtk.Button.do_leave_notify_event(self, *args)

    def do_button_press_event(self, *args):
        self.mousedown = True
        gtk.Button.do_button_press_event(self, *args)

    def do_button_release_event(self, *args):
        self.mousedown = False
        gtk.Button.do_button_release_event(self, *args)

    def do_expose_event(self, event, arg=None):
        a = self.get_allocation()
        ctx = self.window.cairo_create()
        ctx.rectangle(event.area.x, event.area.y,
                      event.area.width, event.area.height)
        ctx.clip()
        self.draw_button(ctx, a.x, a.y, a.width, a.height)

    def draw_button(self, x, y, width, height): abstract

class CairoCloseButton(CairoSmallButton):
    def __init__(self):
        CairoSmallButton.__init__(self, 14)

    def draw_button(self, ctx, x, y, w, h):
        if self.mouseover:
            alpha = 1
        else:
            alpha = 0.5
        button_source = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                                       w, h)
        bctx = cairo.Context(button_source)
        make_path(bctx, 0, 0, w, h, 5)
        bctx.set_source_rgba(1, 0, 0, alpha)
        bctx.fill()
        bctx.scale(w, h)
        bctx.move_to(0.3, 0.3)
        bctx.line_to(0.7, 0.7)
        bctx.move_to(0.3, 0.7)
        bctx.line_to(0.7, 0.3)
        bctx.set_line_width(2.0/w)
        if self.mousedown and self.mouseover:
            bctx.set_source_rgba(1, 1, 1, 1)
        else:
            bctx.set_source_rgba(1, 1, 1, 0)
        bctx.set_operator(cairo.OPERATOR_SOURCE)
        bctx.stroke()

        ctx.set_source_surface(button_source, x, y)
        ctx.paint()

class CairoPlayPauseButton(CairoSmallButton):
    def __init__(self):
        self.pause = False
        CairoSmallButton.__init__(self, 26)

    def set_pause(self, pause):
        self.pause = pause
        self.queue_draw()

    def draw_button(self, ctx, x, y, w, h):
        if self.mouseover:
            alpha = 1
        else:
            alpha = 0.5
        button_source = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                                       w, h)
        bctx = cairo.Context(button_source)
        if self.mousedown and self.mouseover:
            bctx.set_source_rgba(1, 0.4, 0.2, alpha)
        else:
            bctx.set_source_rgba(1, 1, 1, alpha)
        bctx.scale(w, h)
        bctx.set_operator(cairo.OPERATOR_SOURCE)
        if not self.pause:
            bctx.move_to(0.2, 0.0)
            bctx.line_to(1.0, 0.5)
            bctx.line_to(0.2, 1.0)
            bctx.close_path()
        else:
            bctx.move_to(0.2, 0.1)
            bctx.line_to(0.45, 0.1)
            bctx.line_to(0.45, 0.9)
            bctx.line_to(0.2, 0.9)
            bctx.close_path()
            bctx.move_to(0.55, 0.1)
            bctx.line_to(0.8, 0.1)
            bctx.line_to(0.8, 0.9)
            bctx.line_to(0.55, 0.9)
            bctx.close_path()
        bctx.fill_preserve()
        bctx.set_line_width(2.0/w)
        bctx.set_source_rgba(1, 1, 1, 0)
        bctx.stroke()

        ctx.set_source_surface(button_source, x, y)
        ctx.paint()

class CairoNextButton(CairoSmallButton):
    def __init__(self, previous=False):
        self.previous = previous
        CairoSmallButton.__init__(self, 26)

    def draw_button(self, ctx, x, y, w, h):
        if self.mouseover:
            alpha = 1
        else:
            alpha = 0.5
        button_source = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                                       w, h)
        bctx = cairo.Context(button_source)
        bctx.scale(w, h)

        for p in [0.4, 0.0]:
            if self.previous:
                bctx.move_to(1.0-p, 0.0)
                bctx.line_to(0.4-p, 0.5)
                bctx.line_to(1.0-p, 1.0)
            else:
                bctx.move_to(0.0+p, 0.0)
                bctx.line_to(0.6+p, 0.5)
                bctx.line_to(0.0+p, 1.0)
            bctx.close_path()
            bctx.set_operator(cairo.OPERATOR_SOURCE)
            if self.mousedown and self.mouseover:
                bctx.set_source_rgba(1, 0.4, 0.2, alpha)
            else:
                bctx.set_source_rgba(1, 1, 1, alpha)
            bctx.fill_preserve()
            bctx.set_line_width(2.0/w)
            bctx.set_source_rgba(1, 1, 1, 0)
            bctx.stroke()

        ctx.set_source_surface(button_source, x, y)
        ctx.paint()


class CairoPopup(gtk.Window):
    """CairoPopup is a transparent popup window with rounded corners"""
    __gsignals__ = {"expose-event": "override",
                    "enter-notify-event": "override",
                    "leave-notify-event": "override"}
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DOCK)
        gtk_screen = gtk.gdk.screen_get_default()
        colormap = gtk_screen.get_rgba_colormap()
        if colormap is None:
            colormap = gtk_screen.get_rgb_colormap()
        self.set_colormap(colormap)
        self.set_app_paintable(1)
        self.globals = Globals()
        self._pointer_is_inside = False

        self.alignment = gtk.Alignment(0, 0, 0, 0)
        gtk.Window.add(self, self.alignment)
        self.alignment.show()
        self.pointer = ""
        if self.globals.orient == "h":
            # The direction of the pointer isn't important here we only need
            # the right amount of padding so that the popup has right width and
            # height for placement calculations.
            self.point("down")
        else:
            self.point("left")



    def add(self, child):
        self.alignment.add(child)


    def remove(self, child):
        self.alignment.remove(child)


    def point(self, new_pointer, ap=0):
        self.ap = ap
        p = 7
        a = 10
        if new_pointer != self.pointer:
            self.pointer = new_pointer
            padding = {"up":(p+a, p, p, p),
                       "down":(p, p+a, p, p),
                       "left":(p, p, p+a, p),
                       "right":(p, p, p, p+a)}[self.pointer]
            self.alignment.set_padding(*padding)


    def do_expose_event(self, event):
        self.set_shape_mask()
        w,h = self.get_size()
        self.ctx = self.window.cairo_create()
        # set a clip region for the expose event, XShape stuff
        self.ctx.save()
        if self.is_composited():
            self.ctx.set_source_rgba(1, 1, 1,0)
        else:
            self.ctx.set_source_rgb(0.8, 0.8, 0.8)
        self.ctx.set_operator(cairo.OPERATOR_SOURCE)
        self.ctx.paint()
        self.ctx.restore()
        self.ctx.rectangle(event.area.x, event.area.y,
                           event.area.width, event.area.height)
        self.ctx.clip()
        self.draw_frame(self.ctx, w, h)
        gtk.Window.do_expose_event(self, event)

    def set_shape_mask(self):
        # Set window shape from alpha mask of background image
        w,h = self.get_size()
        if w==0: w = 800
        if h==0: h = 600
        pixmap = gtk.gdk.Pixmap (None, w, h, 1)
        ctx = pixmap.cairo_create()
        ctx.set_source_rgba(0, 0, 0,0)
        ctx.set_operator (cairo.OPERATOR_SOURCE)
        ctx.paint()
        if self.is_composited():
            make_path(ctx, 0, 0, w, h, 6, 0, 9, self.pointer, self.ap)
            ctx.set_source_rgba(1, 1, 1, 1)
        else:
            make_path(ctx, 0, 0, w, h, 6, 1, 9, self.pointer, self.ap)
            ctx.set_source_rgb(0, 0, 0)
        ctx.fill()
        self.shape_combine_mask(pixmap, 0, 0)
        del pixmap

    def draw_frame(self, ctx, w, h):
        color = self.globals.colors["color1"]
        red = float(int(color[1:3], 16))/255
        green = float(int(color[3:5], 16))/255
        blue = float(int(color[5:7], 16))/255
        alpha= float(self.globals.colors["color1_alpha"]) / 255
        make_path(ctx, 0, 0, w, h, 6, 2.5, 9, self.pointer, self.ap)
        if self.is_composited():
            ctx.set_source_rgba(red, green, blue, alpha)
        else:
            ctx.set_source_rgb(red, green, blue)
        ctx.fill_preserve()
        if self.is_composited():
            ctx.set_source_rgba(0.0, 0.0, 0.0, 0.8)
        else:
            ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(3)
        ctx.stroke_preserve()
        if self.is_composited():
            ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        else:
            ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.set_line_width(2)
        ctx.stroke()

    def pointer_is_inside(self):
        ax, ay, width, height = self.alignment.get_allocation()
        top, bottom, left, right = self.alignment.get_padding()
        x, y = self.get_pointer()
        if x >= left and x < width - right and \
           y >= top and y <= height - bottom:
            return True
        else:
            return self._pointer_is_inside

    def do_enter_notify_event(self, *args):
        self._pointer_is_inside = True
        gtk.Window.do_enter_notify_event(self, *args)

    def do_leave_notify_event(self, *args):
        self._pointer_is_inside = False
        gtk.Window.do_leave_notify_event(self, *args)

class CairoWindowButton(gtk.EventBox):
    __gsignals__ = {"clicked": (gobject.SIGNAL_RUN_FIRST,
                                gobject.TYPE_NONE,(gtk.gdk.Event, )),
                    "enter-notify-event": "override",
                    "leave-notify-event": "override",
                    "button-release-event": "override",
                    "button-press-event": "override"}

    def __init__(self, label=None, border_width=5, roundness=5):
        gtk.EventBox.__init__(self)
        self.set_visible_window(False)
        self.set_above_child(False)
        self.area = CairoArea(label, border_width, roundness)
        self.label = self.area.label
        gtk.EventBox.add(self, self.area)
        self.area.show()
        self.mousedown = False
        self.prevent_click = False

    def do_leave_notify_event(self, *args):
        if self.mousedown:
            self.area.set_pressed_down(False)
        self.area.queue_draw()

    def do_enter_notify_event(self, *args):
        if self.mousedown:
            self.area.set_pressed_down(True)
        self.area.queue_draw()

    def add(self, child):
        self.area.add(child)

    def remove(self, child):
        self.area.remove(child)

    def get_child(self):
        return self.area.get_child()

    def set_label(self, text, color=None):
        self.area.set_label(text, color)

    def set_label_color(self, color):
        self.area.set_label_color(color)

    def get_label(self):
        return self.area.text

    def redraw(self):
        self.area.queue_draw()

    def do_button_release_event(self, event):
        if self.area.pointer_is_inside() and not self.prevent_click:
            self.emit("clicked", event)
        self.area.set_pressed_down(False)
        self.mousedown=False
        self.prevent_click = False

    def do_button_press_event(self, event):
        if self.area.pointer_is_inside() and not self.prevent_click:
            self.mousedown = True
            self.area.set_pressed_down(True)

    def disable_click(self, *args):
        # A "hack" to avoid CairoWindowButton from reacting to clicks on
        # buttons inside the CairoWindowButton. (The button on top should
        # have it's press-button-event connected to this function.)
        self.area.set_pressed_down(False)
        self.mousedown = False
        self.prevent_click = True

class CairoWindowItem(CairoWindowButton):
    __gsignals__ = {"close-clicked": (gobject.SIGNAL_RUN_FIRST,
                                gobject.TYPE_NONE,())}
    def __init__(self, name, icon, big_icon):
        CairoWindowButton.__init__(self)
        self.globals = Globals()
        self.window_name = name
        self.icon = icon
        self.big_icon = big_icon
        self.minimized = False
        self.is_active_window = False
        self.needs_attention = False


        self.close_button = CairoCloseButton()
        self.close_button.set_no_show_all(True)
        if self.globals.settings["show_close_button"]:
            self.close_button.show()
        self.label = gtk.Label()
        self.label.set_ellipsize(ELLIPSIZE_END)
        self.label.set_alignment(0, 0.5)
        self.__update_label_state()
        hbox = gtk.HBox()
        self.icon_image = gtk.image_new_from_pixbuf(self.icon)
        hbox.pack_start(self.icon_image, False)
        hbox.pack_start(self.label, True, True, padding = 4)
        alignment = gtk.Alignment(1, 0.5, 0, 0)
        alignment.add(self.close_button)
        hbox.pack_start(alignment, False, False)

        vbox = gtk.VBox()
        vbox.pack_start(hbox, False)
        self.preview_box = gtk.Alignment(0.5, 0.5, 0, 0)
        self.preview_box.set_padding(4, 2, 0, 0)
        self.preview =  gtk.Image()
        self.preview_box.add(self.preview)
        self.preview.show()
        vbox.pack_start(self.preview_box, True, True)
        self.add(vbox)
        self.preview_box.set_no_show_all(True)
        vbox.show_all()

        self.close_button.connect("button-press-event", self.disable_click)
        self.close_button.connect("clicked", self.__on_close_button_clicked)
        connect(self.globals, "show-close-button-changed",
                             self.__on_show_close_button_changed)
        connect(self.globals, "color-changed", self.__update_label_state)

    def __on_close_button_clicked(self, *args):
        self.emit("close-clicked")

    def __on_show_close_button_changed(self, *args):
        if self.globals.settings["show_close_button"]:
            self.close_button.show()
        else:
            self.close_button.hide()
            self.label.queue_resize()

    def __update_label_state(self, arg=None):
        """Updates the style of the label according to window state."""
        text = escape(str(self.window_name))
        if self.needs_attention:
            text = "<i>"+text+"</i>"
        if self.is_active_window:
            color = self.globals.colors["color3"]
        elif self.minimized:
            color = self.globals.colors["color4"]
        else:
            color = self.globals.colors["color2"]
        text = "<span foreground=\"" + color + "\">" + text + "</span>"
        self.label.set_text(text)
        self.label.set_use_markup(True)
        # The label should be 140px wide unless there are more room
        # because the preview takes up more.
        self.label.set_size_request(140, -1)

    def __make_minimized_icon(self, icon):
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True,
                                          8, icon.get_width(),
                                          icon.get_height())
        pixbuf.fill(0x00000000)
        minimized_icon = pixbuf.copy()
        icon.composite(pixbuf, 0, 0, pixbuf.get_width(),
                         pixbuf.get_height(), 0, 0, 1, 1,
                         gtk.gdk.INTERP_BILINEAR, 190)
        pixbuf.saturate_and_pixelate(minimized_icon, 0.12, False)
        return minimized_icon

    def get_preview_allocation(self):
        return self.preview.get_allocation()

    def set_needs_attention(self, needs_attention):
        self.needs_attention = needs_attention
        self.__update_label_state()

    def set_minimized(self, minimized):
        self.minimized = minimized
        if self.minimized:
            pixbuf = self.__make_minimized_icon(self.icon)
            self.icon_image.set_from_pixbuf(pixbuf)
            self.preview.set_from_pixbuf(self.big_icon)
        else:
            self.icon_image.set_from_pixbuf(self.icon)
            self.preview.clear()
        self.__update_label_state()

    def set_icon(self, icon, big_icon):
        self.icon = icon
        self.big_icon = big_icon
        if self.minimized:
            pixbuf = self.make_minimized_icon(icon)
            self.icon_image.set_from_pixbuf(pixbuf)
        else:
            self.icon_image.set_from_pixbuf(self.icon)

    def set_name(self, name):
        self.window_name = name
        self.__update_label_state()

    def set_is_active_window(self, is_active):
        self.is_active_window = is_active
        self.__update_label_state()

    def set_preview_aspect(self, width, height, ar=1.0):
        size = self.globals.settings["preview_size"]
        if width*ar < size and height < size:
            pass
        elif float(width) / height > ar:
            height = int(size * ar * height / width)
            width = int(size * ar)
        else:
            width = size * width / height
            height = size
        self.preview.set_size_request(width, height)
        return width, height

    def set_show_preview(self, show_preview):
        if show_preview:
            self.preview_box.show()
        else:
            self.preview_box.hide()

    def set_highlighted(self, highlighted):
        self.area.set_highlighted(highlighted)


class CairoArea(gtk.Alignment):
    """CairoButton is a gtk button with a cairo surface painted over it."""
    __gsignals__ = {"expose-event" : "override"}
    def __init__(self, text=None, border_width=5, roundness=5):
        self.r = roundness
        self.b = border_width
        self.text = text
        gtk.Alignment.__init__(self, 0, 0, 1, 1)
        self.set_padding(self.b, self.b, self.b, self.b)
        self.set_app_paintable(1)
        self.globals = Globals()
        self.highlighted = False
        if text:
            self.label = gtk.Label()
            self.add(self.label)
            self.label.show()
            color = self.globals.colors["color2"]
            self.set_label(text, color)
        else:
            self.label = None

    def set_label(self, text, color=None):
        self.text = text
        if color:
            text = "<span foreground=\"" + color + "\">" + escape(text) + \
                   "</span>"
        self.label.set_text(text)
        self.label.set_use_markup(True)
        self.label.set_use_underline(True)

    def set_label_color(self, color):
        label = "<span foreground=\"" + color + "\">" + escape(self.text) + \
                "</span>"
        self.label.set_text(label)
        self.label.set_use_markup(True)
        self.label.set_use_underline(True)

    def do_expose_event(self, event, arg=None):
        a = self.get_allocation()
        mx , my = self.get_pointer()
        if (mx >= 0 and mx < a.width and my >= 0 and my < a.height) or \
            self.highlighted:
            ctx = self.window.cairo_create()
            ctx.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
            ctx.clip()
            self.draw_frame(ctx, a.x, a.y, a.width, a.height, self.r)
        self.propagate_expose(self.get_child(), event)
        return

    def draw_frame(self, ctx, x, y, w, h, roundness=6, border_color="#FFFFFF"):
        if self.is_composited():
            r, g, b = parse_color(self.globals.colors["color1"])
            alpha = parse_alpha(self.globals.colors["color1_alpha"])
        else:
            r = g = b = 0.0
            alpha = 0.25
        make_path(ctx, x, y, w, h, roundness)


        ctx.set_source_rgba(r, g, b, alpha)
        ctx.fill_preserve()

        r, g, b = parse_color(border_color)
        ctx.set_source_rgba(r, g, b, 0.8)
        ctx.set_line_width(1)
        ctx.stroke()

    def set_pressed_down(self, pressed):
        if pressed:
            self.set_padding(self.b + 1, self.b - 1, self.b, self.b)
        else:
            self.set_padding(self.b, self.b, self.b, self.b)


    def set_highlighted(self, highlighted):
        self.highlighted = highlighted
        self.queue_draw()

    def pointer_is_inside(self):
        mx,my = self.get_pointer()
        a = self.get_allocation()

        if mx >= 0 and mx < a.width \
        and my >= 0 and my < a.height:
            # Mouse pointer is inside the "rectangle"
            # but check if it's still outside the rounded corners
            x = None
            y = None
            r = self.r
            if mx < r:
                x = r - mx
            if (a.width - mx) < r:
                x = mx - (a.width - r)
            if my < r:
                y = r - my
            if (a.height - my) < r:
                y = my - (a.height - r)
            if x is None or y is None \
            or (x**2 + y**2) < (r-1)**2:
                return True
        else:
            return False


class CairoMenuItem(CairoWindowButton):
    def __init__(self, label):
        CairoWindowButton.__init__(self, label)
        self.area.set_padding(3, 3, 5, 5)

class CairoToggleMenu(gtk.VBox):
    __gsignals__ = {"toggled": (gobject.SIGNAL_RUN_FIRST,
                                gobject.TYPE_NONE,(bool, ))}

    def __init__(self, label=None, show_menu=False):
        gtk.VBox.__init__(self)
        self.globals = Globals()

        self.set_spacing(0)
        self.set_border_width(0)
        self.toggle_button = CairoMenuItem(label)
        if label:
            if show_menu:
                color = self.globals.colors["color4"]
            else:
                color = self.globals.colors["color2"]
            self.toggle_button.set_label(label, color)
        self.pack_start(self.toggle_button)
        self.toggle_button.show()
        self.toggle_button.connect("clicked", self.toggle)
        self.menu = CairoVBox()
        self.pack_start(self.menu)
        self.menu.set_border_width(10)
        self.show_menu = show_menu
        if show_menu:
            self.menu.show()

    def add_item(self, item):
        self.menu.pack_start(item)

    def remove_item(self, item):
        self.menu.remove(item)

    def get_items(self):
        return self.menu.get_children()

    def toggle(self, *args):
        if self.show_menu:
            self.menu.hide()
            color = self.globals.colors["color2"]
        else:
            self.menu.show()
            color = self.globals.colors["color4"]
        if self.toggle_button.label:
            self.toggle_button.set_label_color(color)
        self.show_menu = not self.show_menu
        self.emit("toggled", self.show_menu)


class CairoVBox(gtk.VBox):
    __gsignals__ = {"expose-event" : "override"}

    def __init__(self, label=None, show_menu=False):
        gtk.VBox.__init__(self)
        self.globals = Globals()

    def do_expose_event(self, event, arg=None):
        a = self.get_allocation()
        ctx = self.window.cairo_create()
        ctx.rectangle(event.area.x, event.area.y,
                      event.area.width, event.area.height)
        ctx.clip()
        self.draw_frame(ctx, a.x, a.y, a.width, a.height, 6)
        for child in self.get_children():
            self.propagate_expose(child, event)

    def draw_frame(self, ctx, x, y, w, h, roundness=6, color="#000000"):
        r, g, b = parse_color(color)

        make_path(ctx, x, y, w, h, roundness)
        ctx.set_source_rgba(r, g, b, 0.20)
        ctx.fill_preserve()

        ctx.set_source_rgba(r, g, b, 0.20)
        ctx.set_line_width(1)
        ctx.stroke()

def make_path(ctx, x=0, y=0, w=0, h=0, r=6, b=0.5,
              arrow_size=0, arrow_direction=None, arrow_position=0):
    a = arrow_size
    ap = arrow_position
    lt = x + b
    rt = x + w - b
    up = y + b
    dn = y + h - b

    if arrow_direction == "up":
        up += a
    if arrow_direction == "down":
        dn -= a
    if arrow_direction == "left":
        lt += a
    if arrow_direction == "right":
        rt -= a
    ctx.move_to(lt, up + r)
    ctx.arc(lt + r, up + r, r, -pi, -pi/2)
    if arrow_direction == "up":
        ctx.line_to (ap-a, up)
        ctx.line_to(ap, up-a)
        ctx.line_to(ap+a, up)
    ctx.arc(rt - r, up + r, r, -pi/2, 0)
    if arrow_direction == "right":
        ctx.line_to (rt, ap-a)
        ctx.line_to(rt+a, ap)
        ctx.line_to(rt, ap+a)
    ctx.arc(rt - r, dn - r, r, 0, pi/2)
    if arrow_direction == "down":
        ctx.line_to (ap+a, dn)
        ctx.line_to(ap, dn+a)
        ctx.line_to(ap-a, dn)
    ctx.arc(lt + r, dn - r, r, pi/2, pi)
    if arrow_direction == "left":
        ctx.line_to (lt, ap+a)
        ctx.line_to(lt-a, ap)
        ctx.line_to(lt, ap-a)
    ctx.close_path()

def parse_color(color):
    r = float(int(color[1:3], 16))/255
    g = float(int(color[3:5], 16))/255
    b = float(int(color[5:7], 16))/255
    return r, g, b

def parse_alpha(alpha):
    return float(alpha)/255

