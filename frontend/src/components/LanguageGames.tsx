import React, { useState } from 'react';
import './LanguageGames.css';

interface LanguageGamesProps {
  selectedLanguage: string;
}

interface GameData {
  game_type: string;
  title: string;
  questions?: QuizQuestion[];
  phrases?: PronunciationPhrase[];
  pairs?: WordPair[];
}

interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
}

interface PronunciationPhrase {
  text: string;
  phonetic: string;
  difficulty: string;
  tip: string;
}

interface WordPair {
  word1: string;
  word2: string;
  category: string;
}

const LanguageGames: React.FC<LanguageGamesProps> = ({ selectedLanguage }) => {
  const [selectedGame, setSelectedGame] = useState<string>('');
  const [difficulty, setDifficulty] = useState<string>('easy');
  const [gameData, setGameData] = useState<GameData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [score, setScore] = useState(0);
  const [showResult, setShowResult] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [gameCompleted, setGameCompleted] = useState(false);

  // Word Match Game State
  const [selectedCards, setSelectedCards] = useState<number[]>([]);
  const [matchedPairs, setMatchedPairs] = useState<number[]>([]);
  const [shuffledCards, setShuffledCards] = useState<string[]>([]);

  const getGameTypes = () => {
    const gameTypeMap: { [key: string]: any } = {
      'en': [
        { id: 'vocabulary_quiz', name: '📚 Vocabulary Quiz', description: 'Choose the correct meaning from options' },
        { id: 'pronunciation_practice', name: '🗣️ Pronunciation Practice', description: 'Learn correct pronunciation' },
        { id: 'word_match', name: '🔗 Word Matching', description: 'Match words with their meanings' }
      ],
      'ja': [
        { id: 'vocabulary_quiz', name: '📚 語彙クイズ', description: '単語の意味を選択肢から選ぶ' },
        { id: 'pronunciation_practice', name: '🗣️ 発音練習', description: '正しい発音を学ぶ' },
        { id: 'word_match', name: '🔗 単語マッチング', description: '単語とその意味をマッチさせる' }
      ],
      'zh': [
        { id: 'vocabulary_quiz', name: '📚 词汇测验', description: '从选项中选择正确的含义' },
        { id: 'pronunciation_practice', name: '🗣️ 发音练习', description: '学习正确的发音' },
        { id: 'word_match', name: '🔗 词汇匹配', description: '将词汇与其含义匹配' }
      ],
      'es': [
        { id: 'vocabulary_quiz', name: '📚 Quiz de Vocabulario', description: 'Elige el significado correcto de las opciones' },
        { id: 'pronunciation_practice', name: '🗣️ Práctica de Pronunciación', description: 'Aprende la pronunciación correcta' },
        { id: 'word_match', name: '🔗 Emparejamiento de Palabras', description: 'Empareja palabras con sus significados' }
      ],
      'fr': [
        { id: 'vocabulary_quiz', name: '📚 Quiz de Vocabulaire', description: 'Choisissez le bon sens parmi les options' },
        { id: 'pronunciation_practice', name: '🗣️ Pratique de Prononciation', description: 'Apprenez la bonne prononciation' },
        { id: 'word_match', name: '🔗 Correspondance de Mots', description: 'Associez les mots à leurs significations' }
      ],
      'de': [
        { id: 'vocabulary_quiz', name: '📚 Vokabel-Quiz', description: 'Wählen Sie die richtige Bedeutung aus den Optionen' },
        { id: 'pronunciation_practice', name: '🗣️ Aussprache-Übung', description: 'Lernen Sie die richtige Aussprache' },
        { id: 'word_match', name: '🔗 Wort-Zuordnung', description: 'Ordnen Sie Wörter ihren Bedeutungen zu' }
      ],
      'it': [
        { id: 'vocabulary_quiz', name: '📚 Quiz di Vocabolario', description: 'Scegli il significato corretto dalle opzioni' },
        { id: 'pronunciation_practice', name: '🗣️ Pratica di Pronuncia', description: 'Impara la pronuncia corretta' },
        { id: 'word_match', name: '🔗 Abbinamento di Parole', description: 'Abbina le parole ai loro significati' }
      ],
      'el': [
        { id: 'vocabulary_quiz', name: '📚 Κουίζ Λεξιλογίου', description: 'Επιλέξτε τη σωστή έννοια από τις επιλογές' },
        { id: 'pronunciation_practice', name: '🗣️ Εξάσκηση Προφοράς', description: 'Μάθετε τη σωστή προφορά' },
        { id: 'word_match', name: '🔗 Αντιστοίχιση Λέξεων', description: 'Αντιστοιχίστε λέξεις με τις έννοιές τους' }
      ],
      'he': [
        { id: 'vocabulary_quiz', name: '📚 חידון אוצר מילים', description: 'בחר את המשמעות הנכונה מהאפשרויות' },
        { id: 'pronunciation_practice', name: '🗣️ תרגול הגייה', description: 'למד את ההגייה הנכונה' },
        { id: 'word_match', name: '🔗 התאמת מילים', description: 'התאם מילים למשמעויותיהן' }
      ]
    };
    
    return gameTypeMap[selectedLanguage] || gameTypeMap['en'];
  };

  const gameTypes = getGameTypes();

  const getGameHeaderText = () => {
    const headerMap: { [key: string]: string } = {
      'en': 'Language Games',
      'ja': '語学ゲーム',
      'zh': '语言游戏',
      'es': 'Juegos de Idiomas',
      'fr': 'Jeux de Langue',
      'de': 'Sprachspiele',
      'it': 'Giochi di Lingua',
      'el': 'Παιχνίδια Γλώσσας',
      'he': 'משחקי שפה'
    };
    return headerMap[selectedLanguage] || headerMap['en'];
  };

  const getSelectionText = () => {
    const selectionMap: { [key: string]: string } = {
      'en': 'Please select a game',
      'ja': 'ゲームを選択してください',
      'zh': '请选择一个游戏',
      'es': 'Por favor selecciona un juego',
      'fr': 'Veuillez sélectionner un jeu',
      'de': 'Bitte wählen Sie ein Spiel',
      'it': 'Seleziona un gioco',
      'el': 'Παρακαλώ επιλέξτε ένα παιχνίδι',
      'he': 'אנא בחר משחק'
    };
    return selectionMap[selectedLanguage] || selectionMap['en'];
  };

  const getDifficultyText = () => {
    const difficultyMap: { [key: string]: { [key: string]: string } } = {
      'en': { easy: 'Easy', medium: 'Medium', hard: 'Hard', difficulty: 'Difficulty:' },
      'ja': { easy: '簡単', medium: '普通', hard: '難しい', difficulty: '難易度:' },
      'zh': { easy: '简单', medium: '中等', hard: '困难', difficulty: '难度:' },
      'es': { easy: 'Fácil', medium: 'Medio', hard: 'Difícil', difficulty: 'Dificultad:' },
      'fr': { easy: 'Facile', medium: 'Moyen', hard: 'Difficile', difficulty: 'Difficulté:' },
      'de': { easy: 'Einfach', medium: 'Mittel', hard: 'Schwer', difficulty: 'Schwierigkeit:' },
      'it': { easy: 'Facile', medium: 'Medio', hard: 'Difficile', difficulty: 'Difficoltà:' },
      'el': { easy: 'Εύκολο', medium: 'Μέτριο', hard: 'Δύσκολο', difficulty: 'Δυσκολία:' },
      'he': { easy: 'קל', medium: 'בינוני', hard: 'קשה', difficulty: 'רמת קושי:' }
    };
    return difficultyMap[selectedLanguage] || difficultyMap['en'];
  };

  const getGameSetupText = () => {
    const setupMap: { [key: string]: string } = {
      'en': 'Game Setup',
      'ja': 'ゲーム設定',
      'zh': '游戏设置',
      'es': 'Configuración del Juego',
      'fr': 'Configuration du Jeu',
      'de': 'Spiel-Einstellungen',
      'it': 'Impostazioni Gioco',
      'el': 'Ρυθμίσεις Παιχνιδιού',
      'he': 'הגדרות משחק'
    };
    return setupMap[selectedLanguage] || setupMap['en'];
  };

  const getLoadingText = () => {
    const loadingMap: { [key: string]: string } = {
      'en': 'Generating game...',
      'ja': 'ゲーム生成中...',
      'zh': '正在生成游戏...',
      'es': 'Generando juego...',
      'fr': 'Génération du jeu...',
      'de': 'Spiel wird generiert...',
      'it': 'Generazione gioco...',
      'el': 'Δημιουργία παιχνιδιού...',
      'he': 'יוצר משחק...'
    };
    return loadingMap[selectedLanguage] || loadingMap['en'];
  };

  const getStartGameText = () => {
    const startMap: { [key: string]: string } = {
      'en': 'Start Game',
      'ja': 'ゲーム開始',
      'zh': '开始游戏',
      'es': 'Iniciar Juego',
      'fr': 'Commencer le Jeu',
      'de': 'Spiel starten',
      'it': 'Inizia Gioco',
      'el': 'Έναρξη Παιχνιδιού',
      'he': 'התחל משחק'
    };
    return startMap[selectedLanguage] || startMap['en'];
  };

  const getBackText = () => {
    const backMap: { [key: string]: string } = {
      'en': 'Back',
      'ja': '戻る',
      'zh': '返回',
      'es': 'Volver',
      'fr': 'Retour',
      'de': 'Zurück',
      'it': 'Indietro',
      'el': 'Πίσω',
      'he': 'חזור'
    };
    return backMap[selectedLanguage] || backMap['en'];
  };

  const getGameCompletedText = () => {
    const completedMap: { [key: string]: string } = {
      'en': 'Game Completed!',
      'ja': 'ゲーム完了！',
      'zh': '游戏完成！',
      'es': '¡Juego Completado!',
      'fr': 'Jeu Terminé !',
      'de': 'Spiel Abgeschlossen!',
      'it': 'Gioco Completato!',
      'el': 'Παιχνίδι Ολοκληρώθηκε!',
      'he': 'המשחק הושלם!'
    };
    return completedMap[selectedLanguage] || completedMap['en'];
  };

  const getPlayAgainText = () => {
    const playAgainMap: { [key: string]: string } = {
      'en': 'Play Again',
      'ja': 'もう一度プレイ',
      'zh': '再玩一次',
      'es': 'Jugar de Nuevo',
      'fr': 'Rejouer',
      'de': 'Nochmal spielen',
      'it': 'Gioca Ancora',
      'el': 'Παίξε Ξανά',
      'he': 'שחק שוב'
    };
    return playAgainMap[selectedLanguage] || playAgainMap['en'];
  };

  const getExitGameText = () => {
    const exitMap: { [key: string]: string } = {
      'en': 'Exit Game',
      'ja': 'ゲーム終了',
      'zh': '退出游戏',
      'es': 'Salir del Juego',
      'fr': 'Quitter le Jeu',
      'de': 'Spiel beenden',
      'it': 'Esci dal Gioco',
      'el': 'Έξοδος από το Παιχνίδι',
      'he': 'צא מהמשחק'
    };
    return exitMap[selectedLanguage] || exitMap['en'];
  };

  const generateGame = async () => {
    if (!selectedGame) return;

    setIsLoading(true);
    setGameCompleted(false);
    setCurrentQuestion(0);
    setScore(0);
    setShowResult(false);
    setSelectedAnswer(null);

    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/games/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          game_type: selectedGame,
          language_code: selectedLanguage,
          difficulty: difficulty,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setGameData(data);

        // Initialize word match game
        if (selectedGame === 'word_match' && data.pairs) {
          initializeWordMatchGame(data.pairs);
        }
      } else {
        alert('ゲームの生成に失敗しました。');
      }
    } catch (error) {
      console.error('Error generating game:', error);
      alert('ゲーム生成中にエラーが発生しました。');
    } finally {
      setIsLoading(false);
    }
  };

  const initializeWordMatchGame = (pairs: WordPair[]) => {
    const cards: string[] = [];
    pairs.forEach(pair => {
      cards.push(pair.word1, pair.word2);
    });
    
    // Shuffle cards
    const shuffled = [...cards].sort(() => Math.random() - 0.5);
    setShuffledCards(shuffled);
    setSelectedCards([]);
    setMatchedPairs([]);
  };

  const handleQuizAnswer = (answerIndex: number) => {
    setSelectedAnswer(answerIndex);
    setShowResult(true);

    if (gameData?.questions && answerIndex === gameData.questions[currentQuestion].correct_answer) {
      setScore(score + 1);
    }

    setTimeout(() => {
      if (gameData?.questions && currentQuestion < gameData.questions.length - 1) {
        setCurrentQuestion(currentQuestion + 1);
        setSelectedAnswer(null);
        setShowResult(false);
      } else {
        setGameCompleted(true);
      }
    }, 2000);
  };

  const handleCardClick = (cardIndex: number) => {
    if (selectedCards.includes(cardIndex) || matchedPairs.includes(cardIndex)) {
      return;
    }

    const newSelected = [...selectedCards, cardIndex];
    setSelectedCards(newSelected);

    if (newSelected.length === 2) {
      const [first, second] = newSelected;
      const firstCard = shuffledCards[first];
      const secondCard = shuffledCards[second];

      // Check if cards match
      const isMatch = gameData?.pairs?.some(pair => 
        (pair.word1 === firstCard && pair.word2 === secondCard) ||
        (pair.word1 === secondCard && pair.word2 === firstCard)
      );

      setTimeout(() => {
        if (isMatch) {
          setMatchedPairs([...matchedPairs, first, second]);
          setScore(score + 1);
          
          // Check if game is completed
          if (matchedPairs.length + 2 === shuffledCards.length) {
            setGameCompleted(true);
          }
        }
        setSelectedCards([]);
      }, 1000);
    }
  };

  const resetGame = () => {
    setSelectedGame('');
    setGameData(null);
    setCurrentQuestion(0);
    setScore(0);
    setShowResult(false);
    setSelectedAnswer(null);
    setGameCompleted(false);
    setSelectedCards([]);
    setMatchedPairs([]);
    setShuffledCards([]);
  };

  const renderVocabularyQuiz = () => {
    if (!gameData?.questions) return null;

    const question = gameData.questions[currentQuestion];

    return (
      <div className="quiz-container">
        <div className="quiz-header">
          <h3>{gameData.title}</h3>
          <div className="progress">
            問題 {currentQuestion + 1} / {gameData.questions.length}
          </div>
          <div className="score">スコア: {score}</div>
        </div>

        <div className="question-container">
          <h4>{question.question}</h4>
          <div className="options">
            {question.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleQuizAnswer(index)}
                className={`option ${
                  showResult
                    ? index === question.correct_answer
                      ? 'correct'
                      : index === selectedAnswer
                      ? 'incorrect'
                      : ''
                    : ''
                }`}
                disabled={showResult}
              >
                {option}
              </button>
            ))}
          </div>

          {showResult && (
            <div className="explanation">
              <p><strong>説明:</strong> {question.explanation}</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderPronunciationPractice = () => {
    if (!gameData?.phrases) return null;

    return (
      <div className="pronunciation-container">
        <h3>{gameData.title}</h3>
        <div className="phrases-list">
          {gameData.phrases.map((phrase, index) => (
            <div key={index} className="phrase-card">
              <div className="phrase-text">{phrase.text}</div>
              <div className="phonetic">{phrase.phonetic}</div>
              <div className="difficulty-badge">{phrase.difficulty}</div>
              <div className="tip">{phrase.tip}</div>
              <button 
                className="practice-btn"
                onClick={() => {
                  const utterance = new SpeechSynthesisUtterance(phrase.text);
                  utterance.lang = selectedLanguage === 'ja' ? 'ja-JP' : selectedLanguage;
                  speechSynthesis.speak(utterance);
                }}
              >
                🔊 発音を聞く
              </button>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderWordMatchGame = () => {
    if (!gameData?.pairs || shuffledCards.length === 0) return null;

    return (
      <div className="word-match-container">
        <h3>{gameData.title}</h3>
        <div className="match-score">マッチした組: {score} / {gameData.pairs.length}</div>
        
        <div className="cards-grid">
          {shuffledCards.map((card, index) => (
            <button
              key={index}
              onClick={() => handleCardClick(index)}
              className={`match-card ${
                selectedCards.includes(index) ? 'selected' : ''
              } ${
                matchedPairs.includes(index) ? 'matched' : ''
              }`}
              disabled={matchedPairs.includes(index)}
            >
              {card}
            </button>
          ))}
        </div>
      </div>
    );
  };

  const renderGameCompleted = () => {
    const totalQuestions = gameData?.questions?.length || gameData?.pairs?.length || 0;
    const percentage = Math.round((score / totalQuestions) * 100);

    return (
      <div className="game-completed">
        <h3>🎉 {getGameCompletedText()}</h3>
        <div className="final-score">
          <div className="score-circle">
            <span className="score-number">{score}</span>
            <span className="score-total">/ {totalQuestions}</span>
          </div>
          <div className="percentage">{percentage}%</div>
        </div>
        <button onClick={resetGame} className="play-again-btn">
          {getPlayAgainText()}
        </button>
      </div>
    );
  };

  return (
    <div className="language-games">
      <div className="games-header">
        <h2>🎮 {getGameHeaderText()}</h2>
      </div>

      {!selectedGame ? (
        <div className="game-selection">
          <h3>{getSelectionText()}</h3>
          <div className="game-types">
            {gameTypes.map((game: any) => (
              <div
                key={game.id}
                onClick={() => setSelectedGame(game.id)}
                className="game-type-card"
              >
                <h4>{game.name}</h4>
                <p>{game.description}</p>
              </div>
            ))}
          </div>
        </div>
      ) : !gameData ? (
        <div className="game-setup">
          <h3>{getGameSetupText()}</h3>
          <div className="difficulty-selection">
            <label>{getDifficultyText().difficulty}</label>
            <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
              <option value="easy">{getDifficultyText().easy}</option>
              <option value="medium">{getDifficultyText().medium}</option>
              <option value="hard">{getDifficultyText().hard}</option>
            </select>
          </div>
          <div className="setup-buttons">
            <button onClick={generateGame} disabled={isLoading} className="start-btn">
              {isLoading ? getLoadingText() : getStartGameText()}
            </button>
            <button onClick={resetGame} className="back-btn">{getBackText()}</button>
          </div>
        </div>
      ) : gameCompleted ? (
        renderGameCompleted()
      ) : (
        <div className="game-content">
          {selectedGame === 'vocabulary_quiz' && renderVocabularyQuiz()}
          {selectedGame === 'pronunciation_practice' && renderPronunciationPractice()}
          {selectedGame === 'word_match' && renderWordMatchGame()}
          
          <button onClick={resetGame} className="exit-btn">
            {getExitGameText()}
          </button>
        </div>
      )}
    </div>
  );
};

export default LanguageGames;
