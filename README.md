# squirrelchat-final-bugfree
For this portion of the assignment, you will complete our chat server by building a web frontend for the server. The web frontend will offer the following functionality:

- Creating new accounts

- Allowing users to change passwords on existing accounts

- Allowing the user to view logs of channels that haven’t been encrypted (and from which they haven’t been banned):
  - Users should be able to log in and see the list of available channels hosted on the server
  - Users should be able to see the channel topic
  - They should also see the list of files available on the channel, including the file name and file size. If they have the correct privileges (either the person who uploaded it or the channel admin) they should be able to delete it.
  - Users should be able to download the files from the server.
  - Users should be able to upload files to the server.

- Allowing users to manage their block lists, blocking and unblocking other users.

- Allowing channel administrators to perform various operations on channels:
  - Give other users administration privileges
  - Change the channel topic
  - Ban users from channels

# Design Details
You should implement your web frontend using some web framework, though I do not care which. If you have implemented the previous parts of projects 1G and 2G correctly, you should leverage your implementation in those parts to complete 3G. Specifically, you should have your server set up so that you run the web server using flask, and run the chat server alongside that web server, but on a different port. I would specifically recommend either using Flask or Django for this project.

Note that you will need some way for the web frontend and the chat server to agree on some amount of the data. For example, they both need to be able to read logs of channels for various users. You have a few options for how to go about this: you could set up the web frontend so that it talked to the chat server by sending packets according to the protocol, for instance. But that’s not a very robust design. A better design–and the one I recommend–is to have your chat server and web server both share some database implemented using an SQL server (SQLite is fine for this project).

For example, you may want to restructure your chat server so that it keeps the password database as an SQL table. In the web interface, you should have a form that allows the user to create a new account and–if its not in the table–salts and hashes it using the same exact mechanism you use from project 2G. I recommend having a shared set of library code (i.e., helper functions you use in both codebases) between the client and server to make this easier. Then, in the chat server, when a connection is received and an authenticate command is executed, check for the password in that SQLite table.

Similar modifications will need to be made with other commands.

If you do choose to base your implementation off the horribly-insecure example app I’ve written, you should absolutely read the documentation for Flask for a while before just brazenly charging along and copying the bad coding style there. Specifically, reconnecting to the DB every time is silly and terrible form done for illustrative purposes of writing a crummy exploitable app. Instead, for example, read this page on using SQLite with Flask. Similar tutorials exist for PostgreSQL and MySQL.

# Scoring Breakdown
Your server should include at least the following:

- [x] [10 points] You have some webservice that runs alongside your chat server. This is the bare minimum you can do, and I recommend tackling this part first. The way to start with this is to take the example code I’ve given out for the Flask attacks and then run your chat server alongside it.

- [x] [10 points] The web app must run via HTTPS with some certificate. It’s okay if this certificate is self-signed, though (you won’t be able to get a “real” certificate, because you’ll just be running the app on your own browser and won’t be able to anchor it to a specific domain).

- [x] [15 points] The ability to log in and create an account on the server. This infrastructure works alongside the infrastructure used in your chat server.

- [x] [10 points] The ability for users to change their passwords once logged in.

- [x] [15 points] After users are logged in, they should see a page that allows them see all of the channels on the server from which they are not banned. Channels of which they are the administrator should be designated in some special way (e.g., with an “A” letter before the name, or colored green, or something like that). In particular, they should not see channels from which they have been banned.

- [x] [5 points] Users should be able to create new channels from the main screen.

- [x] [10 points] Each channel should have a screen in the app which is viewable by anyone who has not been banned from the channel. This screen should show the log of chats on the channel, up to the 500 most recent messages. This screen should also list the files associated with the channel.

- [x] [5 points] Users should be able to download files associated with a channel from this screen.

- [x] [5 points] Users should be able to upload files associated with the channel from this screen.

- [x] [5 points] Administrators on this channel should have the option to change the channel topic, as well as give administration privileges to other users. These privileges should be reflected in the client.

- [x] [5 points] Administrators should be able to ban users on channels of which they are administrators.

- [X] [10 points] Write a design document of at least four thoughtful paragraphs describing various security issues you thought over while designing your server. The kinds of questions you’ve been asking on Piazza, and the kinds of questions you’ve asked to each other in person, are the kinds of things you want to discuss here. For example, how did you make sure to avoid SQL injection and cross-site scripting attacks? This can be as broad or narrow as you want, as long as it’s thoughtful and covers the security-relevant problems you tackled while working on the project.

Note that you must be especially careful to make sure that changes made on the server are reflected in the client. For example, if someone is banned from a channel in the webapp, they should similarly be kicked from the channel if they are logged in on the web server. This is probably the trickiest part of the assignment, and you’ll have to be careful about how you implement it.

Note that various parts of 2G make things encrypted in various ways. You’ll have to use your head here: it doesn’t make any sense to show logs for encrypted channels, for example, because the server won’t have the keys to decrypt them. If you did this, you should also have some “public channels” that allow their logs to be viewable without crypto, too.

There is no need to show private messages on the web interface. In an ideal world, you would write a web app that allowed the client to decrypt the conversation: i.e., JavaScript code that hands the conversation to your client, uses the client’s secret key (stored in the browser, but never escaping it) to decrypt messages, etc.. But in practice this is quite complicated: browsers don’t make it easy to manage keys and access local files, for example. Therefore, for this project, you can feel free to ignore anything that would require you to load a secret key from the client’s browser. However, all of that should still work on your client that you implemented for 2G.

This part of the project is meant to be challenging, so make sure you start early and think through a good design for the server, paying particular caution to how you’ll ensure your client from 2G still works with the chat server you’re implementing.