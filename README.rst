armstrong.core.arm_wells
========================
Provides the basic content well code necessary for scheduling and arranging
models inside ArmstrongCMS. Conceptually, a well is an ordered grouping of
content that can expire.

.. warning:: This is development level software.  Please do not unless you are
             familiar with what that means and are comfortable using that type
             of software.

Installation
------------

::

    NAME=armstrong.core.arm_wells
    pip install -e git://github.com/armstrong/$NAME.git#egg=$NAME


Usage
-----

Wells utilize GenericForeignKeys to associate content with themselves, so any
model can be placed in a well, regardless of if it inherits from
armstrong.core.arm_content.models.ContentBase

Wells can also be backed by a queryset which will be used as a source of
additional content after all items have been exhausted. Currently, this is not
configurable via the admin, but is easily accomplished by using the
QuerySetBackedWellView. In your urls.py:

    url(r'^$', QuerySetBackedWellView.as_view(well_title='front_page',
                                              template_name="index.html",
                                              queryset=Article.published.all()),
            name='front_page'),
    # get's the current 'front_page' well, backs it with Article.published.all()
    # and renders the index.html page

To render a well we recommend using the armstrong.core.arm_layout module. This
will allow simple templates to handle heterogenous content. For instance, to
render ever item in a well using the 'standard' layout:

    {% load layout_helpers %}
    {% for content in well.items %}
        {% render_model content 'standard' %}
    {% endfor %}


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
