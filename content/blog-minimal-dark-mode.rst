=============================
This blog: now with dark mode
=============================

:date: 2022-11-10 09:00
:tags: en


What is the best way to simulate some novelty when you haven't blogged for four
years? You change your blog's appearance a bit. Having read `"Minimal Dark Mode"
<https://meiert.com/en/blog/minimal-dark-mode/>`_, I wondered how good the
described minimal dark mode would work on my blog. As it turns out: suprisingly
well. At least considered the minimal effort it took. In this post, I will
sketch out how I added it to my theme.


First: a minimal dark theme
===========================

The beauty of this solution: the dark theme gets automatically created from the
light theme.

.. code-block:: css

   html, img:not([src$='.svg']) {
       filter: invert(1) hue-rotate(180deg);
   }

Invert, do some colour magic, done. This could be wrapped in a media query, so
all visitors who prefer a dark color scheme would see a dark version of this
blog.


A light/dark toggle
===================

Due to the laziness^W minimalism of the dark theme, some visitors might prefer
the light mode, even if their system settings express a preference for dark
mode. So I also wanted a button which toggles the dark mode.

To do so, I first put the above rule into a class:

.. code-block:: css

   .force-dark-theme {
       filter: invert(1) hue-rotate(180deg);
   }

Then a JavaScript function that adds or removes the class:

.. code-block:: javascript

   function toggleDark() {
       document.documentElement.classList.toggle("force-dark-theme");
   }

Finally, a button that calls the function:

.. code-block:: html

   <a href="javascript:toggleDark();"><span class="glyphicon glyphicon-adjust"></span></a>

With that, a visitor can now toggle dark or light mode on a page. Unfortunately,
whenever a new page is loaded, it starts with light mode again. So the visitor's
choice needs to be persisted:

.. code-block:: javascript

   function toggleDark() {
       const forceDark = document.documentElement.classList.toggle("force-dark-theme");
       localStorage.setItem("force-dark", forceDark.toString());
   }

On page load, the preference needs to be loaded and applied:

.. code-block:: javascript

   const forceDark = localStorage.getItem("force-dark");
   if (forceDark === "true") {
       document.documentElement.classList.add("force-dark-theme");
   }

That makes a usable dark mode toggle already. Visitors with a preference for
dark themes in their system settings should see the dark version though, if they
don't click on the toggle button. This can be done with a slight modification:

.. code-block:: javascript

   const forceDark = localStorage.getItem("force-dark");
   const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");
   if (forceDark === null && prefersDark.matches || forceDark === "true") {
       document.documentElement.classList.add("force-dark-theme");
   }

And finally: add an animation when the switch from light to dark or vice versa
happens manually. First, the CSS animation:

.. code-block:: css

   .filter-animation {
       transition-property: filter;
       transition-duration: 1s;
   }

Then the modified ``toggleDark`` function:

.. code-block:: javascript

   function toggleDark() {
       document.documentElement.classList.add("filter-animation");
       const forceDark = document.documentElement.classList.toggle("force-dark-theme");
       localStorage.setItem("force-dark", forceDark.toString());
   }
