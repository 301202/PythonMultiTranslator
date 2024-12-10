import { useRouter } from 'next/router';
import { useState } from 'react';

export default function Home() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name) return alert("Please enter your name!");

    const route = isCreating ? '/api/create-room' : '/api/join-room';
    const response = await fetch(route, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, code }),
    });

    if (response.ok) {
      const data = await response.json();
      router.push(`/room/${data.room}`);
    } else {
      alert('Error: ' + (await response.text()));
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
      {!isCreating && <input placeholder="Room Code" value={code} onChange={(e) => setCode(e.target.value)} />}
      <button type="submit">{isCreating ? 'Create Room' : 'Join Room'}</button>
      <button type="button" onClick={() => setIsCreating(!isCreating)}>
        {isCreating ? 'Switch to Join' : 'Switch to Create'}
      </button>
    </form>
  );
}
