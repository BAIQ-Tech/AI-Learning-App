import React, { useState } from 'react';
import styled from 'styled-components';
import { FaCheck, FaTimes } from 'react-icons/fa';
import { Lesson, Exercise } from '../types';
import { languageApi } from '../services/api';

// FaPlay is imported for future use
const FaPlay = () => null;

const LessonContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const LessonHeader = styled.div`
  text-align: center;
  margin-bottom: 32px;
`;

const LessonTitle = styled.h2`
  color: #2d3748;
  margin-bottom: 8px;
`;

const LessonLevel = styled.span`
  background: #667eea;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  text-transform: uppercase;
  font-weight: 600;
`;

const Section = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h3`
  color: #4a5568;
  margin-bottom: 16px;
  border-bottom: 2px solid #e1e5e9;
  padding-bottom: 8px;
`;

const VocabularyGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
`;

const VocabularyCard = styled.div`
  background: #f7fafc;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
`;

const VocabularyWord = styled.div`
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 4px;
`;

const VocabularyTranslation = styled.div`
  color: #718096;
  margin-bottom: 4px;
`;

const VocabularyPronunciation = styled.div`
  font-style: italic;
  color: #a0aec0;
  font-size: 14px;
`;

const ExamplesList = styled.ul`
  list-style: none;
  padding: 0;
`;

const ExampleItem = styled.li`
  background: #edf2f7;
  padding: 12px 16px;
  margin-bottom: 8px;
  border-radius: 6px;
  border-left: 3px solid #48bb78;
`;

const GrammarBox = styled.div`
  background: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 8px;
  padding: 20px;
`;

const GrammarPoint = styled.h4`
  color: #c53030;
  margin-bottom: 12px;
`;

const GrammarExplanation = styled.p`
  color: #4a5568;
  line-height: 1.6;
`;

const ExerciseCard = styled.div`
  background: #f0fff4;
  border: 1px solid #c6f6d5;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
`;

const ExerciseQuestion = styled.div`
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 12px;
`;

const ExerciseInput = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e1e5e9;
  border-radius: 4px;
  margin-bottom: 8px;
`;

const OptionButton = styled.button<{ selected?: boolean; correct?: boolean; incorrect?: boolean }>`
  display: block;
  width: 100%;
  padding: 10px 16px;
  margin-bottom: 8px;
  border: 2px solid ${props => 
    props.correct ? '#48bb78' : 
    props.incorrect ? '#e53e3e' : 
    props.selected ? '#667eea' : '#e1e5e9'};
  background: ${props => 
    props.correct ? '#c6f6d5' : 
    props.incorrect ? '#fed7d7' : 
    props.selected ? '#ebf4ff' : 'white'};
  color: ${props => 
    props.correct ? '#22543d' : 
    props.incorrect ? '#742a2a' : '#2d3748'};
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  
  &:hover {
    background: ${props => 
      props.correct ? '#c6f6d5' : 
      props.incorrect ? '#fed7d7' : '#f7fafc'};
  }
`;

const CheckButton = styled.button`
  background: #48bb78;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  
  &:hover {
    background: #38a169;
  }
  
  &:disabled {
    background: #a0aec0;
    cursor: not-allowed;
  }
`;

const FeedbackMessage = styled.div<{ correct: boolean }>`
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  background: ${props => props.correct ? '#c6f6d5' : '#fed7d7'};
  color: ${props => props.correct ? '#22543d' : '#742a2a'};
  display: flex;
  align-items: center;
  gap: 8px;
`;

const GenerateLessonButton = styled.button`
  width: 100%;
  padding: 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 20px;
  
  &:hover {
    background: #5a67d8;
  }
  
  &:disabled {
    background: #a0aec0;
    cursor: not-allowed;
  }
`;

const LevelSelector = styled.select`
  padding: 8px 12px;
  border: 1px solid #e1e5e9;
  border-radius: 4px;
  margin-right: 12px;
`;

interface LessonViewerProps {
  selectedLanguage: string;
}

const LessonViewer: React.FC<LessonViewerProps> = ({ selectedLanguage }) => {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedLevel, setSelectedLevel] = useState<'beginner' | 'intermediate' | 'advanced'>('beginner');
  const [exerciseAnswers, setExerciseAnswers] = useState<{ [key: number]: string }>({});
  const [exerciseFeedback, setExerciseFeedback] = useState<{ [key: number]: { correct: boolean; message: string } }>({});

  const generateLesson = async () => {
    if (!selectedLanguage) return;

    setIsLoading(true);
    try {
      const newLesson = await languageApi.generateLesson(selectedLanguage, selectedLevel);
      setLesson(newLesson);
      setExerciseAnswers({});
      setExerciseFeedback({});
    } catch (error) {
      console.error('Failed to generate lesson:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const checkExercise = (exerciseIndex: number, exercise: Exercise) => {
    const userAnswer = exerciseAnswers[exerciseIndex];
    if (!userAnswer) return;

    const correct = userAnswer.toLowerCase().trim() === exercise.answer.toLowerCase().trim();
    setExerciseFeedback(prev => ({
      ...prev,
      [exerciseIndex]: {
        correct,
        message: correct ? 'Correct! Well done!' : `Incorrect. The correct answer is: ${exercise.answer}`
      }
    }));
  };

  const handleMultipleChoice = (exerciseIndex: number, option: string, exercise: Exercise) => {
    setExerciseAnswers(prev => ({ ...prev, [exerciseIndex]: option }));
    
    const correct = option === exercise.answer;
    setExerciseFeedback(prev => ({
      ...prev,
      [exerciseIndex]: {
        correct,
        message: correct ? 'Correct! Well done!' : `Incorrect. The correct answer is: ${exercise.answer}`
      }
    }));
  };

  return (
    <LessonContainer>
      <div style={{ marginBottom: '20px', textAlign: 'center' }}>
        <LevelSelector 
          value={selectedLevel} 
          onChange={(e) => setSelectedLevel(e.target.value as any)}
        >
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </LevelSelector>
        
        <GenerateLessonButton
          onClick={generateLesson}
          disabled={isLoading || !selectedLanguage}
        >
          {isLoading ? 'Generating Lesson...' : 'Generate New Lesson'}
        </GenerateLessonButton>
      </div>

      {lesson && (
        <>
          <LessonHeader>
            <LessonTitle>{lesson.title}</LessonTitle>
            <LessonLevel>{lesson.level}</LessonLevel>
          </LessonHeader>

          <Section>
            <SectionTitle>Vocabulary</SectionTitle>
            <VocabularyGrid>
              {lesson.vocabulary.map((item, index) => (
                <VocabularyCard key={index}>
                  <VocabularyWord>{item.word}</VocabularyWord>
                  <VocabularyTranslation>{item.translation}</VocabularyTranslation>
                  <VocabularyPronunciation>{item.pronunciation}</VocabularyPronunciation>
                </VocabularyCard>
              ))}
            </VocabularyGrid>
          </Section>

          <Section>
            <SectionTitle>Example Sentences</SectionTitle>
            <ExamplesList>
              {lesson.examples.map((example, index) => (
                <ExampleItem key={index}>{example}</ExampleItem>
              ))}
            </ExamplesList>
          </Section>

          <Section>
            <SectionTitle>Grammar Point</SectionTitle>
            <GrammarBox>
              <GrammarPoint>{lesson.grammar.point}</GrammarPoint>
              <GrammarExplanation>{lesson.grammar.explanation}</GrammarExplanation>
            </GrammarBox>
          </Section>

          <Section>
            <SectionTitle>Practice Exercises</SectionTitle>
            {lesson.exercises.map((exercise, index) => (
              <ExerciseCard key={index}>
                <ExerciseQuestion>{exercise.question}</ExerciseQuestion>
                
                {exercise.type === 'multiple-choice' ? (
                  <div>
                    {exercise.options?.map((option, optionIndex) => (
                      <OptionButton
                        key={optionIndex}
                        selected={exerciseAnswers[index] === option}
                        correct={exerciseFeedback[index] && option === exercise.answer}
                        incorrect={exerciseFeedback[index] && exerciseAnswers[index] === option && option !== exercise.answer}
                        onClick={() => handleMultipleChoice(index, option, exercise)}
                      >
                        {option}
                      </OptionButton>
                    ))}
                  </div>
                ) : (
                  <div>
                    <ExerciseInput
                      type="text"
                      value={exerciseAnswers[index] || ''}
                      onChange={(e) => setExerciseAnswers(prev => ({ ...prev, [index]: e.target.value }))}
                      placeholder="Type your answer here..."
                    />
                    <CheckButton
                      onClick={() => checkExercise(index, exercise)}
                      disabled={!exerciseAnswers[index]}
                    >
                      Check Answer
                    </CheckButton>
                  </div>
                )}
                
                {exerciseFeedback[index] && (
                  <FeedbackMessage correct={exerciseFeedback[index].correct}>
                    {exerciseFeedback[index].correct ? <FaCheck /> : <FaTimes />}
                    {exerciseFeedback[index].message}
                  </FeedbackMessage>
                )}
              </ExerciseCard>
            ))}
          </Section>
        </>
      )}
    </LessonContainer>
  );
};

export default LessonViewer;
