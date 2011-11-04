armstrong.core.arm_wells
========================
Provides the basic content well code necessary for scheduling and arranging
models inside Armstrong. Conceptually, a well is an ordered grouping of
content that can expire.

.. warning:: This is development level software.  Please do not unless you are
             familiar with what that means and are comfortable using that type
             of software.

Installation
------------

::

    NAME=armstrong.core.arm_wells
    pip install -e git://github.com/armstrong/$NAME.git#egg=$NAME


Introduction
------------
Wells are one of the most powerful components in Armstrong; they are
fundamentally about the ordering and structuring of content.

Frequently there are parts of the site that simply display the most recently
published stories that belong to some grouping (a section or tag for
instance), but when there are big stories, editorial staff wants to feature
them by placing them at the top. Wells allow editorial staff to pin stories
through the admin. The demo project uses a QuerysetBackedWellView to accomplish
this use case with the 'front_page' WellType.

``armstrong.core.arm_wells`` provides 3 primary objects to work with. The
highest level is a WellType, which is generally a specific location on your
site where you'd like to order content. Each WellType has a number of Well
objects. A Well object represents a specific ordering of content for that
WellType for a certain period of time. Every Well has a number of Node objects
each of which relates the Well to an object in the database through a
GenericForeignKey.


Ordering Arbitrary Content
--------------------------
The simplest way to use wells is with just one Well object associated
with a WellType. Changing the content of that Well or how that content is
ordered will immediately change what is displayed on the site.

The use of GenericForeignKeys to link Node objects to content gives you a lot
of flexibility. Wells make it easy to feature data apps, videos, audio clips,
photo galleries and liveblogs all in one well even if there is no common base
class for all their object.

The challenge of laying out various content objects with different styling and
fields spurred the development of ``armstrong.core.arm_layout`` which provides
a framework for specifying named layouts for your various content objects.

By thinking of wells as just simple tools for ordering content, you'll start
seeing other places on your site where they're a good fit.  Anything that has
objects in the database that the writing or editorial staff would like to
reorder on the site is a good candidate for wells.


Scheduling
----------
The other major aspect to Wells is scheduling. If the editorial staff wants to
plan the front page for Thursday at 5pm, they can create a new Well with the
'front_page' WellType and the content they want displayed. By setting the new
Well's pub_date for 5pm Thursday, no action will need to be taken at that time,
the site will just start using the new Well.

Similarly Well's have an expires field if content should only be scheduled for
a certain period of time and then revert to an earlier well. We recommend that
every WellType have an empty Well object that never expires to provide a sane
fallback.

The WellManager has a convenience method, get_current, that takes in a WellType
name and fetches the Well associated with that WellType, has the most recent
pub_date in the past and doesn't have an expires in the past.

Using a QuerySetBackedWellView
------------------------------
Wells can also be backed by a queryset which will be used as a source of
additional content after all items have been exhausted. Currently, this is not
configurable via the admin, but can be easily accomplished by using the
``QuerySetBackedWellView``. For example, in a urls.py::

    url(r'^$', QuerySetBackedWellView.as_view(well_title='front_page',
                                              template_name="index.html",
                                              queryset=Article.published.all()),
            name='front_page'),
    # get's the current 'front_page' well, backs it with Article.published.all()
    # and renders the index.html page

To render a well we recommend using the ``armstrong.core.arm_layout module``.
This will allow simple templates to handle heterogenous content. For instance,
to render every item in a well using the 'standard' layout::

    {% load layout_helpers %}
    {% for content in well.items %}
        {% render_model content 'standard' %}
    {% endfor %}

Admin Customization
-------------------
The admin view for modifying a well has been customized to provide a drag and
drop interface for ordering Node's. To add a Node to a well, use the
VisualSearch box to first search for a ContentType and then for the title of
the object you want to use. For instance, in the demo, type 'art' into the box
which will provide 'ARTICLE', press enter and search for articles with 'Perry' in
the title. The VisualSearch widget is from ``armstrong.hatband``, which
provides more information about customizing that process.

When a node is added, it displays simple (and not particularly helpful)
information about it's ContentType id and object id. It also sends a request to
the server for the html result of a render_model call with the 'preview' name.
This allows you to easily display the nodes in a manner similar to how those
objects will display on the site.

Contributing
------------
* Create something awesome -- make the code better, add some functionality,
  whatever (this is the hardest part).
* `Fork it`_
* Create a topic branch to house your changes
* Get all of your commits in the new topic branch
* Submit a `pull request`_


State of Project
----------------
Armstrong is an open-source news platform that is freely available to any
organization.  It is the result of a collaboration between the `Texas Tribune`_
and `Bay Citizen`_, and a grant from the `John S. and James L. Knight
Foundation`_.  The first release is scheduled for June, 2011.

To follow development, be sure to join the `Google Group`_.

``armstrong.core.arm_wells`` is part of the `Armstrong`_ project.  You're
probably looking for that.


License
-------
Copyright 2011 Bay Citizen and Texas Tribune

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

.. _Armstrong: http://www.armstrongcms.org/
.. _Bay Citizen: http://www.baycitizen.org/
.. _John S. and James L. Knight Foundation: http://www.knightfoundation.org/
.. _Texas Tribune: http://www.texastribune.org/
.. _Google Group: http://groups.google.com/group/armstrongcms
.. _pull request: http://help.github.com/pull-requests/
.. _Fork it: http://help.github.com/forking/
