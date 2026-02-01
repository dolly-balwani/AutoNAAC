import { useState, useEffect } from 'react';
import { Button } from '../UI';

/**
 * TextEditor Component
 * 
 * Rich text editing area for narrative content with word count
 * and action buttons.
 * 
 * @param {Object} props
 * @param {string} props.content - Initial content
 * @param {Function} props.onChange - Content change handler
 * @param {Function} props.onRegenerate - Regenerate button handler
 * @param {Function} props.onImprove - Improve button handler
 * @param {Function} props.onSave - Save button handler
 * @param {boolean} props.isLoading - Loading state for actions
 */
function TextEditor({ 
  content = '', 
  onChange, 
  onRegenerate, 
  onImprove, 
  onSave,
  isLoading = false 
}) {
  const [text, setText] = useState(content);
  const [wordCount, setWordCount] = useState(0);
  const [charCount, setCharCount] = useState(0);

  // Update counts when text changes
  useEffect(() => {
    const words = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
    const chars = text.length;
    setWordCount(words);
    setCharCount(chars);
  }, [text]);

  // Sync with prop changes
  useEffect(() => {
    setText(content);
  }, [content]);

  /**
   * Handle text changes
   */
  const handleChange = (e) => {
    const newText = e.target.value;
    setText(newText);
    if (onChange) {
      onChange(newText);
    }
  };

  return (
    <div className="text-editor">
      <textarea
        className="text-editor__textarea"
        value={text}
        onChange={handleChange}
        placeholder="Enter or edit the narrative content here..."
        disabled={isLoading}
      />
      
      <div className="text-editor__toolbar">
        <div className="text-editor__counter">
          <span>{wordCount} words</span>
          <span style={{ marginLeft: '16px' }}>{charCount} characters</span>
        </div>
        
        <div className="text-editor__actions">
          <Button 
            variant="secondary" 
            onClick={onRegenerate}
            disabled={isLoading}
          >
            ↻ Regenerate
          </Button>
          <Button 
            variant="secondary" 
            onClick={onImprove}
            disabled={isLoading}
          >
            ✨ Improve
          </Button>
          <Button 
            variant="primary" 
            onClick={() => onSave(text)}
            disabled={isLoading}
          >
            💾 Save
          </Button>
        </div>
      </div>
    </div>
  );
}

export default TextEditor;
