import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import ImageUpload from './components/ImageUpload';
import QuestionInput from './components/QuestionInput';
import ResponseDisplay from './components/ResponseDisplay';
import BackgroundAnimation from './components/BackgroundAnimation';
import './App.css';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow-x: hidden;
`;

const ContentWrapper = styled.div`
  position: relative;
  z-index: 10;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled(motion.header)`
  text-align: center;
  margin-bottom: 3rem;
`;

const Title = styled(motion.h1)`
  font-size: 3.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const Subtitle = styled(motion.p)`
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0;
  font-weight: 300;
`;

const MainContent = styled(motion.div)`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
`;

const Card = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    border-color: rgba(255, 255, 255, 0.3);
  }
`;

const LoadingOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const LoadingSpinner = styled(motion.div)`
  width: 60px;
  height: 60px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

interface AnalysisResponse {
  answer: string;
  model_used: string;
  processing_time: number;
  fallback_used: boolean;
  error?: string;
}

function App() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState<string>('');
  const [question, setQuestion] = useState<string>('');
  const [response, setResponse] = useState<AnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const handleImageSelect = (file: File) => {
    setSelectedImage(file);
    setImageUrl(''); // Clear URL when file is selected
    setError('');
  };

  const handleUrlChange = (url: string) => {
    setImageUrl(url);
    setSelectedImage(null); // Clear file when URL is entered
    setError('');
  };

  const handleQuestionChange = (q: string) => {
    setQuestion(q);
    setError('');
  };

  const handleSubmit = async () => {
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    if (!selectedImage && !imageUrl.trim()) {
      setError('Please select an image or enter an image URL');
      return;
    }

    setIsLoading(true);
    setError('');
    setResponse(null);

    try {
      let result: AnalysisResponse;

      if (selectedImage) {
        // Upload file
        const formData = new FormData();
        formData.append('file', selectedImage);
        formData.append('question', question);

        const uploadResponse = await fetch('/upload', {
          method: 'POST',
          body: formData,
        });

        if (!uploadResponse.ok) {
          throw new Error(`Upload failed: ${uploadResponse.statusText}`);
        }

        result = await uploadResponse.json();
      } else {
        // Analyze URL
        const urlResponse = await fetch('/analyze-url', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: question,
            image_url: imageUrl,
          }),
        });

        if (!urlResponse.ok) {
          throw new Error(`URL analysis failed: ${urlResponse.statusText}`);
        }

        result = await urlResponse.json();
      }

      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut"
      }
    }
  };

  return (
    <AppContainer>
      <BackgroundAnimation />
      
      <ContentWrapper>
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <Header>
            <Title variants={itemVariants}>
              Multimodal QA
            </Title>
            <Subtitle variants={itemVariants}>
              Ask questions about images using AI vision models
            </Subtitle>
          </Header>

          <MainContent variants={itemVariants}>
            <Card
              whileHover={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <ImageUpload
                onImageSelect={handleImageSelect}
                onUrlChange={handleUrlChange}
                selectedImage={selectedImage}
                imageUrl={imageUrl}
              />
            </Card>

            <Card
              whileHover={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <QuestionInput
                question={question}
                onQuestionChange={handleQuestionChange}
                onSubmit={handleSubmit}
                isLoading={isLoading}
                disabled={isLoading}
              />
            </Card>
          </MainContent>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                background: 'rgba(255, 0, 0, 0.1)',
                border: '1px solid rgba(255, 0, 0, 0.3)',
                borderRadius: '10px',
                padding: '1rem',
                marginBottom: '2rem',
                color: '#ff6b6b',
                textAlign: 'center'
              }}
            >
              {error}
            </motion.div>
          )}

          <AnimatePresence>
            {response && (
              <ResponseDisplay response={response} />
            )}
          </AnimatePresence>
        </motion.div>
      </ContentWrapper>

      <AnimatePresence>
        {isLoading && (
          <LoadingOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <LoadingSpinner />
          </LoadingOverlay>
        )}
      </AnimatePresence>
    </AppContainer>
  );
}

export default App;
