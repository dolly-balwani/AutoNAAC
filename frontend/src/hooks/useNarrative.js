import { useState, useCallback } from 'react';

/**
 * Initial narrative content (mock AI-generated text)
 */
const INITIAL_NARRATIVE = `The institution has demonstrated a strong commitment to academic excellence and holistic development of students through various curricular and co-curricular initiatives.

Curriculum Design and Development:
The curriculum is designed in alignment with the UGC guidelines and industry requirements. The institution has successfully implemented the Choice Based Credit System (CBCS) across all programs, providing flexibility to students in course selection. Regular curriculum reviews are conducted with inputs from stakeholders including industry experts, alumni, and academic peers.

Teaching-Learning Process:
The institution employs student-centric teaching methodologies including problem-based learning, case studies, and experiential learning. ICT-enabled classrooms and digital learning resources enhance the teaching-learning experience. Faculty members are encouraged to adopt innovative pedagogical approaches.

Research and Innovation:
The institution promotes a research culture among faculty and students. Research facilities have been augmented with modern equipment and digital resources. Faculty members have published research papers in reputed journals and secured grants from various funding agencies.

Infrastructure and Resources:
The institution has adequate infrastructure facilities including well-equipped laboratories, a comprehensive library with digital resources, and recreational facilities. The campus is Wi-Fi enabled with high-speed internet connectivity.

Student Support:
Various support mechanisms are in place for student welfare including scholarships, career counseling, placement assistance, and grievance redressal. The institution has a dedicated Training and Placement Cell that facilitates industry interactions and campus recruitments.

Quality Assurance:
The Internal Quality Assurance Cell (IQAC) plays a pivotal role in ensuring quality enhancement initiatives. Regular academic audits, feedback analysis, and stakeholder consultations are conducted to maintain and improve institutional quality.`;

/**
 * useNarrative Hook
 * 
 * Manages narrative content state and editing operations.
 * 
 * @returns {Object} Narrative state and methods
 */
export function useNarrative() {
  const [content, setContent] = useState(INITIAL_NARRATIVE);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaved, setIsSaved] = useState(true);
  const [lastSaved, setLastSaved] = useState(null);

  /**
   * Update content
   */
  const updateContent = useCallback((newContent) => {
    setContent(newContent);
    setIsSaved(false);
  }, []);

  /**
   * Regenerate narrative (placeholder for API call)
   */
  const regenerate = useCallback(async () => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const regeneratedContent = `[Regenerated Content]

${INITIAL_NARRATIVE}

Additional sections have been regenerated based on the latest evidence and criteria selections.`;
    
    setContent(regeneratedContent);
    setIsLoading(false);
    setIsSaved(false);
  }, []);

  /**
   * Improve narrative (placeholder for API call)
   */
  const improve = useCallback(async () => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Add some improvements to the content
    const improvedContent = content + `

Enhanced Quality Metrics:
The institution has achieved significant improvements in key performance indicators. Pass percentage has increased by 3% over the assessment period. Research output has shown a 25% increase in publications. Placement statistics reflect an industry-ready workforce with 78% placement rate.`;
    
    setContent(improvedContent);
    setIsLoading(false);
    setIsSaved(false);
  }, [content]);

  /**
   * Save narrative (placeholder for API call)
   */
  const save = useCallback(async (textContent) => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    setContent(textContent);
    setIsSaved(true);
    setLastSaved(new Date().toLocaleTimeString());
    setIsLoading(false);
  }, []);

  return {
    content,
    isLoading,
    isSaved,
    lastSaved,
    updateContent,
    regenerate,
    improve,
    save
  };
}

export default useNarrative;
