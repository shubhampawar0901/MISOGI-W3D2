import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

const Container = styled.div`
  width: 100%;
`;

const SectionTitle = styled.h3`
  color: white;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-align: center;
`;

const TabContainer = styled.div`
  display: flex;
  margin-bottom: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 4px;
`;

const Tab = styled(motion.button)<{ active: boolean }>`
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  background: ${props => props.active ? 'rgba(255, 255, 255, 0.2)' : 'transparent'};
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.15);
  }
`;

const DropzoneContainer = styled(motion.div)<{ isDragActive: boolean; hasFile: boolean }>`
  border: 2px dashed ${props => 
    props.isDragActive ? '#4CAF50' : 
    props.hasFile ? '#2196F3' : 
    'rgba(255, 255, 255, 0.3)'
  };
  border-radius: 15px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  background: ${props => 
    props.isDragActive ? 'rgba(76, 175, 80, 0.1)' : 
    props.hasFile ? 'rgba(33, 150, 243, 0.1)' : 
    'rgba(255, 255, 255, 0.05)'
  };
  
  &:hover {
    border-color: rgba(255, 255, 255, 0.5);
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
  }
`;

const DropzoneText = styled.p`
  color: white;
  margin: 0;
  font-size: 1.1rem;
  font-weight: 400;
`;

const DropzoneSubtext = styled.p`
  color: rgba(255, 255, 255, 0.7);
  margin: 0.5rem 0 0 0;
  font-size: 0.9rem;
`;

const UrlInput = styled(motion.input)`
  width: 100%;
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.6);
  }
  
  &:focus {
    outline: none;
    border-color: #4CAF50;
    background: rgba(255, 255, 255, 0.15);
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
  }
`;

const PreviewContainer = styled(motion.div)`
  margin-top: 1rem;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
`;

const PreviewImage = styled.img`
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  object-fit: contain;
  display: block;
  margin: 0 auto;
`;

const FileName = styled.p`
  color: white;
  margin: 0.5rem 0 0 0;
  text-align: center;
  font-size: 0.9rem;
  opacity: 0.8;
`;

const RemoveButton = styled(motion.button)`
  background: rgba(255, 0, 0, 0.2);
  border: 1px solid rgba(255, 0, 0, 0.4);
  color: #ff6b6b;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 0.5rem;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 0, 0, 0.3);
    transform: scale(1.05);
  }
`;

interface ImageUploadProps {
  onImageSelect: (file: File) => void;
  onUrlChange: (url: string) => void;
  selectedImage: File | null;
  imageUrl: string;
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  onImageSelect,
  onUrlChange,
  selectedImage,
  imageUrl
}) => {
  const [activeTab, setActiveTab] = useState<'upload' | 'url'>('upload');
  const [previewUrl, setPreviewUrl] = useState<string>('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      onImageSelect(file);
      
      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  }, [onImageSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
    },
    multiple: false
  });

  const handleUrlInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    onUrlChange(url);
  };

  const removeImage = () => {
    onImageSelect(null as any);
    setPreviewUrl('');
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
  };

  const removeUrl = () => {
    onUrlChange('');
  };

  return (
    <Container>
      <SectionTitle>Select Image</SectionTitle>
      
      <TabContainer>
        <Tab
          active={activeTab === 'upload'}
          onClick={() => setActiveTab('upload')}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Upload File
        </Tab>
        <Tab
          active={activeTab === 'url'}
          onClick={() => setActiveTab('url')}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Image URL
        </Tab>
      </TabContainer>

      <AnimatePresence mode="wait">
        {activeTab === 'upload' ? (
          <motion.div
            key="upload"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <DropzoneContainer
              {...getRootProps()}
              isDragActive={isDragActive}
              hasFile={!!selectedImage}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <input {...getInputProps()} />
              {isDragActive ? (
                <DropzoneText>Drop the image here...</DropzoneText>
              ) : selectedImage ? (
                <DropzoneText>✓ Image selected: {selectedImage.name}</DropzoneText>
              ) : (
                <>
                  <DropzoneText>📁 Drag & drop an image here</DropzoneText>
                  <DropzoneSubtext>or click to select a file</DropzoneSubtext>
                </>
              )}
            </DropzoneContainer>

            <AnimatePresence>
              {selectedImage && previewUrl && (
                <PreviewContainer
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <PreviewImage src={previewUrl} alt="Preview" />
                  <FileName>{selectedImage.name}</FileName>
                  <div style={{ textAlign: 'center' }}>
                    <RemoveButton
                      onClick={removeImage}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Remove
                    </RemoveButton>
                  </div>
                </PreviewContainer>
              )}
            </AnimatePresence>
          </motion.div>
        ) : (
          <motion.div
            key="url"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <UrlInput
              type="url"
              placeholder="Enter image URL (e.g., https://example.com/image.jpg)"
              value={imageUrl}
              onChange={handleUrlInputChange}
              whileFocus={{ scale: 1.02 }}
            />

            <AnimatePresence>
              {imageUrl && (
                <PreviewContainer
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <PreviewImage 
                    src={imageUrl} 
                    alt="URL Preview"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                  <FileName>Image from URL</FileName>
                  <div style={{ textAlign: 'center' }}>
                    <RemoveButton
                      onClick={removeUrl}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Clear URL
                    </RemoveButton>
                  </div>
                </PreviewContainer>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </Container>
  );
};

export default ImageUpload;
