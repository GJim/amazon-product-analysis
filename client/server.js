/**
 * Redis Pub/Sub Relay Server for Amazon Product Analysis
 * 
 * This server connects to Redis, subscribes to task channels, and relays messages
 * to connected web clients via WebSockets.
 */

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const redis = require('redis');
const path = require('path');

// Configure application
const app = express();
const server = http.createServer(app);
const io = new Server(server);
const PORT = process.env.PORT || 3000;

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Home route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Redis client setup
const redisClient = redis.createClient({
  host: 'localhost',
  port: 6379
});

// Map to keep track of active subscriptions
const activeSubscriptions = new Map();

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('A client connected');
  
  // Handle subscription requests from clients
  socket.on('subscribe', (taskId) => {
    // Format the channel name the same way as in Python
    const channelName = `product_analysis_${taskId}`;
    console.log(`Client subscribing to ${channelName}`);
    
    // Create a subscriber if we don't already have one for this channel
    if (!activeSubscriptions.has(channelName)) {
      console.log(`Creating new subscription for ${channelName}`);
      
      // Create separate Redis client for this subscription
      const subscriber = redis.createClient({
        host: 'localhost',
        port: 6379
      });
      
      subscriber.on('message', (channel, message) => {
        // Relay message to all clients subscribed to this channel
        console.log(`Message received on ${channel}: ${message}`);
        io.to(channelName).emit('message', JSON.parse(message));
      });
      
      // Subscribe to the Redis channel
      subscriber.subscribe(channelName);
      
      // Store subscriber in our map
      activeSubscriptions.set(channelName, {
        subscriber,
        clients: 1
      });
    } else {
      // Increment client count for existing subscription
      const subscription = activeSubscriptions.get(channelName);
      subscription.clients += 1;
      activeSubscriptions.set(channelName, subscription);
    }
    
    // Join the socket.io room for this channel
    socket.join(channelName);
    
    // Confirm subscription to client
    socket.emit('subscribed', channelName);
  });
  
  // Handle unsubscribe events
  socket.on('unsubscribe', (taskId) => {
    const channelName = `product_analysis_${taskId}`;
    
    if (activeSubscriptions.has(channelName)) {
      const subscription = activeSubscriptions.get(channelName);
      subscription.clients -= 1;
      
      // If no more clients, close the subscription
      if (subscription.clients <= 0) {
        console.log(`Closing subscription for ${channelName}`);
        subscription.subscriber.unsubscribe();
        subscription.subscriber.quit();
        activeSubscriptions.delete(channelName);
      } else {
        activeSubscriptions.set(channelName, subscription);
      }
    }
    
    socket.leave(channelName);
    socket.emit('unsubscribed', channelName);
  });
  
  // Handle disconnection
  socket.on('disconnect', () => {
    console.log('Client disconnected');
    // Cleanup would go here in a production app
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});

// Handle Redis connection errors
redisClient.on('error', (err) => {
  console.error('Redis error:', err);
});

// Handle shutdown gracefully
process.on('SIGTERM', () => {
  console.log('Shutting down...');
  
  // Close all subscriptions
  for (const [channelName, subscription] of activeSubscriptions.entries()) {
    subscription.subscriber.unsubscribe();
    subscription.subscriber.quit();
  }
  
  // Close Redis client and server
  redisClient.quit();
  server.close();
  
  process.exit(0);
});
