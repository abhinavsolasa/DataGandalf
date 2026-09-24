import React, { useState } from 'react';

export default function fileUpload({ 
  onUpload,
 } : {
  onUpload: Function;
 }) {
  const [selectedFile, setFile] = useState('');

// On file select (from the pop up)
const onFileChange = (event: any) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
};

// On file upload (click the upload button)
const handleSubmit = (event) => {
    event.preventDefault();
    console.log(selectedFile)

    onUpload(selectedFile);

    // Request made to the backend api
    // Send formData object
};

  return (
    <div>
        <h3>File Upload using React!</h3>
        <div>
            <input
                type="file"
                onChange={onFileChange}
            />
            <button onClick={handleSubmit}>
                Upload!
            </button>
        </div>
    </div>  
  );

  } 

  
