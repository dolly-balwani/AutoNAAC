import { useState, useCallback } from 'react';

/**
 * NAAC Criteria Mock Data
 * Complete list of NAAC criteria and sub-criteria
 */
const CRITERIA_DATA = [
  {
    id: 1,
    name: 'Curricular Aspects',
    description: 'Curriculum design and development',
    subCriteria: [
      { id: '1.1.1', name: 'Curriculum revision and enrichment' },
      { id: '1.1.2', name: 'Percentage of new courses introduced' },
      { id: '1.2.1', name: 'Percentage of programs with CBCS' },
      { id: '1.2.2', name: 'Percentage of programs with electives' },
      { id: '1.3.1', name: 'Cross cutting issues addressed' },
      { id: '1.3.2', name: 'Value added courses offered' },
      { id: '1.4.1', name: 'Feedback analysis and action taken' },
      { id: '1.4.2', name: 'Feedback from employers and alumni' }
    ]
  },
  {
    id: 2,
    name: 'Teaching-Learning and Evaluation',
    description: 'Teaching methodology and student assessment',
    subCriteria: [
      { id: '2.1.1', name: 'Average enrollment percentage' },
      { id: '2.1.2', name: 'Seats filled against reserved categories' },
      { id: '2.2.1', name: 'Student teacher ratio' },
      { id: '2.3.1', name: 'Student centric methods used' },
      { id: '2.3.2', name: 'ICT tools used in teaching' },
      { id: '2.4.1', name: 'Average percentage of full-time teachers' },
      { id: '2.4.2', name: 'Teachers with PhD qualification' },
      { id: '2.5.1', name: 'Mechanism for internal assessment' },
      { id: '2.6.1', name: 'Program outcomes and course outcomes' },
      { id: '2.6.2', name: 'Attainment of POs and COs' }
    ]
  },
  {
    id: 3,
    name: 'Research, Innovations and Extension',
    description: 'Research activities and community engagement',
    subCriteria: [
      { id: '3.1.1', name: 'Research facilities created' },
      { id: '3.1.2', name: 'Seed money for research' },
      { id: '3.2.1', name: 'Grants for research projects' },
      { id: '3.2.2', name: 'Workshops and seminars conducted' },
      { id: '3.3.1', name: 'Research papers published' },
      { id: '3.3.2', name: 'Books and chapters published' },
      { id: '3.4.1', name: 'Extension activities conducted' },
      { id: '3.4.2', name: 'Awards for extension activities' },
      { id: '3.5.1', name: 'Collaborative activities' },
      { id: '3.5.2', name: 'Functional MoUs with institutions' }
    ]
  },
  {
    id: 4,
    name: 'Infrastructure and Learning Resources',
    description: 'Physical and IT infrastructure',
    subCriteria: [
      { id: '4.1.1', name: 'Adequate infrastructure facilities' },
      { id: '4.1.2', name: 'Expenditure on infrastructure' },
      { id: '4.2.1', name: 'Library as a learning resource center' },
      { id: '4.2.2', name: 'E-resources and digital library' },
      { id: '4.3.1', name: 'ICT facilities available' },
      { id: '4.3.2', name: 'Student-computer ratio' },
      { id: '4.4.1', name: 'Expenditure on maintenance' },
      { id: '4.4.2', name: 'Systems and procedures for maintenance' }
    ]
  },
  {
    id: 5,
    name: 'Student Support and Progression',
    description: 'Student welfare and career support',
    subCriteria: [
      { id: '5.1.1', name: 'Students benefited by scholarships' },
      { id: '5.1.2', name: 'Career counseling activities' },
      { id: '5.1.3', name: 'Capacity development programs' },
      { id: '5.2.1', name: 'Students qualified NET/GATE' },
      { id: '5.2.2', name: 'Placement percentage' },
      { id: '5.3.1', name: 'Awards and medals won' },
      { id: '5.3.2', name: 'Student participation in sports/cultural' },
      { id: '5.4.1', name: 'Alumni association activities' },
      { id: '5.4.2', name: 'Alumni contribution to institution' }
    ]
  },
  {
    id: 6,
    name: 'Governance, Leadership and Management',
    description: 'Institutional governance and administration',
    subCriteria: [
      { id: '6.1.1', name: 'Vision and mission of institution' },
      { id: '6.1.2', name: 'Decentralization and participation' },
      { id: '6.2.1', name: 'Strategic plan and deployment' },
      { id: '6.2.2', name: 'E-governance implementation' },
      { id: '6.3.1', name: 'Welfare schemes for staff' },
      { id: '6.3.2', name: 'Faculty development programs' },
      { id: '6.4.1', name: 'Resource mobilization policy' },
      { id: '6.4.2', name: 'Grants received from agencies' },
      { id: '6.5.1', name: 'IQAC contribution' },
      { id: '6.5.2', name: 'Quality initiatives by IQAC' }
    ]
  },
  {
    id: 7,
    name: 'Institutional Values and Best Practices',
    description: 'Institutional ethics and innovations',
    subCriteria: [
      { id: '7.1.1', name: 'Gender equity promotion' },
      { id: '7.1.2', name: 'Environmental consciousness' },
      { id: '7.1.3', name: 'Green campus initiatives' },
      { id: '7.1.4', name: 'Facilities for disabled persons' },
      { id: '7.2.1', name: 'Best practices adopted' },
      { id: '7.3.1', name: 'Institutional distinctiveness' }
    ]
  }
];

/**
 * useCriteria Hook
 * 
 * Manages NAAC criteria selection state.
 * 
 * @returns {Object} Criteria state and methods
 */
export function useCriteria() {
  const [selectAll, setSelectAll] = useState(false);
  const [selectedCriteria, setSelectedCriteria] = useState({});
  
  /**
   * Toggle select all criteria
   */
  const toggleSelectAll = useCallback((checked) => {
    setSelectAll(checked);
    if (checked) {
      // Select all criteria and all sub-criteria
      const allSelected = {};
      CRITERIA_DATA.forEach(criterion => {
        allSelected[criterion.id] = criterion.subCriteria.map(sc => sc.id);
      });
      setSelectedCriteria(allSelected);
    } else {
      setSelectedCriteria({});
    }
  }, []);

  /**
   * Update sub-criteria selection for a specific criterion
   */
  const updateCriteriaSelection = useCallback((criterionId, subCriteriaIds) => {
    setSelectedCriteria(prev => {
      const updated = { ...prev };
      if (subCriteriaIds.length === 0) {
        delete updated[criterionId];
      } else {
        updated[criterionId] = subCriteriaIds;
      }
      return updated;
    });
    
    // Update selectAll if needed
    if (selectAll) {
      setSelectAll(false);
    }
  }, [selectAll]);

  /**
   * Get selected sub-criteria for a specific criterion
   */
  const getSelectedSubCriteria = useCallback((criterionId) => {
    return selectedCriteria[criterionId] || [];
  }, [selectedCriteria]);

  /**
   * Get total count of selected sub-criteria
   */
  const getTotalSelected = useCallback(() => {
    return Object.values(selectedCriteria).reduce((sum, arr) => sum + arr.length, 0);
  }, [selectedCriteria]);

  return {
    criteria: CRITERIA_DATA,
    selectAll,
    selectedCriteria,
    toggleSelectAll,
    updateCriteriaSelection,
    getSelectedSubCriteria,
    getTotalSelected,
    hasSelection: getTotalSelected() > 0
  };
}

export default useCriteria;
