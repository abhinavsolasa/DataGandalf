import React, { useState } from 'react';

export default function SearchBar({ 
  onSearch,
 } : {
  onSearch: Function;
 }) {
  const [query, setQuery] = useState('');

  const inputChange = (event) => {
    setQuery(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Search..."
        value={query}
        onChange={inputChange}
      />
      <button type="submit">Search</button>
    </form>
  );

  } 

  
