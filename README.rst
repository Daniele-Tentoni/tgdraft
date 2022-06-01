-----------------
Cube reunion bot
-----------------
====================================
Organize reunion to draft your cube!
====================================

**Table of contents:**

1. `Purpose`_
2. `Host your own bot`_

Purpose
--------

Utility to manage draft groups.

1. `Register a new cube`_ (you can give a link to `CubeCobra <https://cubecobra.com>`_ page)

2. `Prepare the next draft`_

   a. Set the date (link to Calendar Event)
   b. Set the maximum number of players
   c. Set the whitelist/blacklist

3. `Register to a draft`_

Host your own bot
--------------------

1. Obtain a token
2. Change the name

Functions
----------

.. _`register you as bot user`:

Register as cube reunion user to bot
====================================

To register a player to cube reunion bot, you can send a message in a group with::

   @tgdraft register @user

where ``<chat_id|username>`` could be:

============ ==========
chat_id      Your telegram chat_id
username     Your telegram username
============ ==========

..

     bot_name     Your tgdraft_bot_username

It will ask to that user to send to the bot a private message, activating him. After that, that player can send a private message to the bot with /register <tgdraft_name> to link his telegram_id or telegram_name tgdraft_name to the bot internal database for future cube drafts.

Register a new cube
===================

Send a private message to the bot to register your cube for the next draft. Send him a message with::

   /register_cube <cube_name>

He will ask you to write your cubecobra link if you have one since it's optional. After that he will response you with the resulting id of your cube::

   You have registered a new cube with name `<cube_name>`.

If you have entered a CubeCobra_ link too, the message will look like::

   You have registered a new cube with name `<cube_name>` [CubeCobra](https://cubecobra.com/cube/<cubecobra_cube_id>/overview).

Prepare the next draft
=======================

!!! To register as player in a draft, you have to `register you as bot user`_ first.

In your Telegram group, send a message with a tag to the bot @tgdraft prepare <cube_name> for <players> at <today|tomorrow|future_date> at <hour_of_the_day>. After that, tgdraft will send a message with the list of current partecipants (only you as first time). After that, every one in the group can register him sending a message with @tgdraft sign me for <cube_name|cube_id|cube_short>. The bot will send a message with the updated list of partecipants. To de-register, send a message with @tgdraft kick me, or any admin could kick a player using @tgdraft kick <telegram_id|telegram_name|tgdraft_name>

Any admin could send a private message to @tgdraft with /blacklist <telegram_id|telegram_name|tgdraft_name> <cube_name|cube_id|cube_short> to add a user to the blacklist of that cube. Send a message with /whitelist <telegram_id|telegram_name|tgdraft_name> <cube_name|cube_id|cube_short> to add him to the whitelist. Creating a whitelist will erase the blacklist and viceversa.

Register to a draft
===================

Send a message to @tgdraft_bot or in a group send a message with @tgdraft register me, or if you are an admin of that group, send a message with @tgdraft register @user and tgdraft will send a message to confirm your registration

Any admin may ask to tgdraft bot the list of current registered players by sending a message to @tgdraft_bot with /list_players or in a group send a message with @tgdraft list players.

:Author: Daniele Tentoni <daniele.tentoni.1996@gmail.com>
:Description: Readme for tgdraft_bot git repository
