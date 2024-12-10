import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import io from 'socket.io-client';

let socket;

export default function Room() {
  const router = useRouter();
  const { code } = router.query;
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');

  useEffect(() => {
    socket = io('http://127.0.0.1:5000');
    socket.emit('join', { room: code });

    socket.on('message', (msg) => {
      setMessages((prev) => [...prev, msg]);
    });

    return () => {
      socket.disconnect();
    };
  }, [code]);

  const sendMessage = () => {
    if (message) {
      socket.emit('message', { data: message });
      setMessage('');
    }
  };

  return (
    <div>
      <h1>Room: {code}</h1>
      <div>
        {messages.map((msg, idx) => (
          <p key={idx}><strong>{msg.name}:</strong> {msg.message}</p>
        ))}
      </div>
      <input value={message} onChange={(e) => setMessage(e.target.value)} />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
