import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const Container = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-top: 2rem;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
`;

const Title = styled.h3`
  color: white;
  font-size: 1.5rem;
  margin: 0;
  font-weight: 600;
`;

const MetadataContainer = styled.div`
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
`;

const MetadataBadge = styled(motion.div)<{ variant?: 'success' | 'warning' | 'info' }>`
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  background: ${props => {
    switch (props.variant) {
      case 'success': return 'rgba(76, 175, 80, 0.2)';
      case 'warning': return 'rgba(255, 152, 0, 0.2)';
      case 'info': return 'rgba(33, 150, 243, 0.2)';
      default: return 'rgba(255, 255, 255, 0.1)';
    }
  }};
  border: 1px solid ${props => {
    switch (props.variant) {
      case 'success': return 'rgba(76, 175, 80, 0.4)';
      case 'warning': return 'rgba(255, 152, 0, 0.4)';
      case 'info': return 'rgba(33, 150, 243, 0.4)';
      default: return 'rgba(255, 255, 255, 0.2)';
    }
  }};
  color: ${props => {
    switch (props.variant) {
      case 'success': return '#4CAF50';
      case 'warning': return '#FF9800';
      case 'info': return '#2196F3';
      default: return 'white';
    }
  }};
`;

const AnswerContainer = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-left: 4px solid #4CAF50;
`;

const AnswerText = styled.p`
  color: white;
  font-size: 1.1rem;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
`;

const StatsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
`;

const StatCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
  }
`;

const StatValue = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: #4CAF50;
  margin-bottom: 0.25rem;
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
`;

const FallbackNotice = styled(motion.div)`
  background: rgba(255, 152, 0, 0.1);
  border: 1px solid rgba(255, 152, 0, 0.3);
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
`;

const FallbackIcon = styled.div`
  font-size: 1.5rem;
`;

const FallbackText = styled.div`
  color: #FF9800;
  font-weight: 500;
`;

interface AnalysisResponse {
  answer: string;
  model_used: string;
  processing_time: number;
  fallback_used: boolean;
  error?: string;
}

interface ResponseDisplayProps {
  response: AnalysisResponse;
}

const ResponseDisplay: React.FC<ResponseDisplayProps> = ({ response }) => {
  const formatProcessingTime = (time: number): string => {
    if (time < 1) {
      return `${Math.round(time * 1000)}ms`;
    }
    return `${time.toFixed(2)}s`;
  };

  const getModelDisplayName = (model: string): string => {
    const modelMap: { [key: string]: string } = {
      'gpt-4o': 'GPT-4o (Vision)',
      'claude-3-sonnet': 'Claude 3 Sonnet',
      'gpt-3.5-turbo (fallback)': 'GPT-3.5 Turbo (Text Only)',
      'fallback': 'System Fallback'
    };
    return modelMap[model] || model;
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 30, scale: 0.95 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut",
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    }
  };

  return (
    <Container
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={itemVariants}>
        <Header>
          <Title>🤖 AI Response</Title>
          <MetadataContainer>
            <MetadataBadge 
              variant={response.fallback_used ? 'warning' : 'success'}
              whileHover={{ scale: 1.05 }}
            >
              {getModelDisplayName(response.model_used)}
            </MetadataBadge>
            <MetadataBadge 
              variant="info"
              whileHover={{ scale: 1.05 }}
            >
              {formatProcessingTime(response.processing_time)}
            </MetadataBadge>
          </MetadataContainer>
        </Header>
      </motion.div>

      {response.fallback_used && (
        <motion.div variants={itemVariants}>
          <FallbackNotice
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <FallbackIcon>⚠️</FallbackIcon>
            <FallbackText>
              Vision analysis unavailable - using text-only fallback
            </FallbackText>
          </FallbackNotice>
        </motion.div>
      )}

      <motion.div variants={itemVariants}>
        <AnswerContainer>
          <AnswerText>{response.answer}</AnswerText>
        </AnswerContainer>
      </motion.div>

      <motion.div variants={itemVariants}>
        <StatsContainer>
          <StatCard
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <StatValue>{getModelDisplayName(response.model_used)}</StatValue>
            <StatLabel>Model Used</StatLabel>
          </StatCard>
          
          <StatCard
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <StatValue>{formatProcessingTime(response.processing_time)}</StatValue>
            <StatLabel>Processing Time</StatLabel>
          </StatCard>
          
          <StatCard
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <StatValue>{response.fallback_used ? 'Text Only' : 'Multimodal'}</StatValue>
            <StatLabel>Analysis Type</StatLabel>
          </StatCard>
        </StatsContainer>
      </motion.div>
    </Container>
  );
};

export default ResponseDisplay;
