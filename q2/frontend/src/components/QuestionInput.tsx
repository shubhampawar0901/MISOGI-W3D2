import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const Container = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const SectionTitle = styled.h3`
  color: white;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-align: center;
`;

const TextArea = styled(motion.textarea)`
  width: 100%;
  min-height: 120px;
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
  
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

const ExampleQuestions = styled.div`
  margin-bottom: 1.5rem;
`;

const ExampleTitle = styled.h4`
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  margin-bottom: 0.75rem;
  font-weight: 500;
`;

const ExampleButton = styled(motion.button)`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  margin: 0.25rem;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
`;

const SubmitButton = styled(motion.button)<{ disabled: boolean }>`
  width: 100%;
  padding: 1rem 2rem;
  background: ${props => props.disabled 
    ? 'rgba(255, 255, 255, 0.1)' 
    : 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)'
  };
  border: none;
  border-radius: 15px;
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.3s ease;
  box-shadow: ${props => props.disabled 
    ? 'none' 
    : '0 4px 15px rgba(76, 175, 80, 0.3)'
  };
  
  &:hover {
    ${props => !props.disabled && `
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
    `}
  }
  
  &:active {
    ${props => !props.disabled && `
      transform: translateY(0);
    `}
  }
`;

const CharacterCount = styled.div<{ isNearLimit: boolean }>`
  text-align: right;
  font-size: 0.8rem;
  color: ${props => props.isNearLimit ? '#ff6b6b' : 'rgba(255, 255, 255, 0.6)'};
  margin-top: -1rem;
  margin-bottom: 1rem;
`;

interface QuestionInputProps {
  question: string;
  onQuestionChange: (question: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  disabled: boolean;
}

const QuestionInput: React.FC<QuestionInputProps> = ({
  question,
  onQuestionChange,
  onSubmit,
  isLoading,
  disabled
}) => {
  const maxLength = 500;
  const isNearLimit = question.length > maxLength * 0.8;

  const exampleQuestions = [
    "What objects can you see in this image?",
    "Describe the colors and mood of this image",
    "What is the main subject of this photo?",
    "Can you identify any text in this image?",
    "What's happening in this scene?",
    "What time of day does this appear to be taken?"
  ];

  const handleExampleClick = (example: string) => {
    onQuestionChange(example);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      if (!disabled && question.trim()) {
        onSubmit();
      }
    }
  };

  return (
    <Container>
      <SectionTitle>Ask a Question</SectionTitle>
      
      <TextArea
        placeholder="What would you like to know about this image? Be specific for better results..."
        value={question}
        onChange={(e) => onQuestionChange(e.target.value)}
        onKeyPress={handleKeyPress}
        maxLength={maxLength}
        whileFocus={{ scale: 1.02 }}
        transition={{ type: "spring", stiffness: 300 }}
      />
      
      <CharacterCount isNearLimit={isNearLimit}>
        {question.length}/{maxLength}
      </CharacterCount>

      <ExampleQuestions>
        <ExampleTitle>💡 Example questions:</ExampleTitle>
        {exampleQuestions.map((example, index) => (
          <ExampleButton
            key={index}
            onClick={() => handleExampleClick(example)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: "spring", stiffness: 400 }}
          >
            {example}
          </ExampleButton>
        ))}
      </ExampleQuestions>

      <SubmitButton
        onClick={onSubmit}
        disabled={disabled || !question.trim()}
        whileHover={!disabled && !isLoading ? { scale: 1.02 } : {}}
        whileTap={!disabled && !isLoading ? { scale: 0.98 } : {}}
        transition={{ type: "spring", stiffness: 400 }}
      >
        {isLoading ? (
          <motion.div
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <motion.div
              style={{
                width: '20px',
                height: '20px',
                border: '2px solid rgba(255, 255, 255, 0.3)',
                borderTop: '2px solid white',
                borderRadius: '50%',
                marginRight: '10px'
              }}
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            />
            Analyzing...
          </motion.div>
        ) : (
          '🔍 Analyze Image'
        )}
      </SubmitButton>
      
      <div style={{ 
        textAlign: 'center', 
        marginTop: '0.5rem', 
        fontSize: '0.8rem', 
        color: 'rgba(255, 255, 255, 0.6)' 
      }}>
        Press Ctrl+Enter to submit
      </div>
    </Container>
  );
};

export default QuestionInput;
