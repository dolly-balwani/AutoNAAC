import { useState, useCallback } from 'react';

/**
 * Mock Evidence Data
 * Sample extracted evidence for demonstration
 */
const MOCK_TEXT_EVIDENCE = [
  {
    sourceFile: 'Annual_Report_2024.pdf',
    pageNumber: 12,
    content: 'The institution has implemented Choice Based Credit System (CBCS) across all undergraduate and postgraduate programs since the academic year 2020-21. This system allows students to choose courses based on their interests and career goals.'
  },
  {
    sourceFile: 'IQAC_Minutes.docx',
    pageNumber: 3,
    content: 'The Internal Quality Assurance Cell has conducted 15 workshops on quality enhancement initiatives during the assessment period. Faculty members participated in various FDPs organized by UGC-HRDC.'
  },
  {
    sourceFile: 'Research_Publications.pdf',
    pageNumber: 8,
    content: 'A total of 245 research papers were published in UGC-CARE listed journals during the assessment period. The institution encourages faculty to pursue interdisciplinary research collaborations.'
  },
  {
    sourceFile: 'Infrastructure_Report.pdf',
    pageNumber: 5,
    content: 'The campus is equipped with 50+ ICT-enabled classrooms, 8 computer laboratories with 400+ systems, and high-speed internet connectivity of 1 Gbps. All classrooms are equipped with LCD projectors and audio systems.'
  },
  {
    sourceFile: 'Placement_Data.xlsx',
    pageNumber: 1,
    content: 'During 2023-24, 78% of eligible students were placed through campus recruitment. Top recruiters include TCS, Infosys, Wipro, and various PSUs. The average package offered was 5.2 LPA.'
  }
];

const MOCK_IMAGE_EVIDENCE = [
  {
    sourceFile: 'Campus_Photos.pdf',
    pageNumber: 2,
    content: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"><rect fill="%23e5e7eb" width="400" height="200"/><text x="200" y="100" text-anchor="middle" fill="%236b7280" font-size="14">Campus Main Building</text></svg>',
    description: 'Main administrative building'
  },
  {
    sourceFile: 'Lab_Photos.pdf',
    pageNumber: 5,
    content: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"><rect fill="%23e5e7eb" width="400" height="200"/><text x="200" y="100" text-anchor="middle" fill="%236b7280" font-size="14">Computer Laboratory</text></svg>',
    description: 'State-of-the-art computer lab'
  },
  {
    sourceFile: 'Library_Photos.pdf',
    pageNumber: 1,
    content: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"><rect fill="%23e5e7eb" width="400" height="200"/><text x="200" y="100" text-anchor="middle" fill="%236b7280" font-size="14">Central Library</text></svg>',
    description: 'Digital library section'
  }
];

const MOCK_TABLE_EVIDENCE = [
  {
    sourceFile: 'Student_Data.xlsx',
    pageNumber: 1,
    headers: ['Year', 'Enrolled', 'Passed', 'Pass %'],
    rows: [
      ['2021-22', '1250', '1180', '94.4%'],
      ['2022-23', '1320', '1265', '95.8%'],
      ['2023-24', '1400', '1358', '97.0%']
    ]
  },
  {
    sourceFile: 'Faculty_Details.xlsx',
    pageNumber: 1,
    headers: ['Department', 'Professors', 'Associate Prof.', 'Assistant Prof.'],
    rows: [
      ['Computer Science', '5', '8', '12'],
      ['Electronics', '4', '6', '10'],
      ['Mechanical', '6', '9', '14'],
      ['Civil', '4', '7', '11']
    ]
  },
  {
    sourceFile: 'Research_Grants.xlsx',
    pageNumber: 1,
    headers: ['Funding Agency', 'Project Count', 'Amount (Lakhs)'],
    rows: [
      ['UGC', '8', '45.5'],
      ['DST', '5', '62.3'],
      ['AICTE', '12', '38.7'],
      ['Industry', '6', '85.2']
    ]
  }
];

/**
 * useEvidence Hook
 * 
 * Manages evidence data state and filtering.
 * 
 * @returns {Object} Evidence state and methods
 */
export function useEvidence() {
  const [activeTab, setActiveTab] = useState('text');
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Get evidence data based on active tab
   */
  const getEvidence = useCallback(() => {
    switch (activeTab) {
      case 'text':
        return MOCK_TEXT_EVIDENCE;
      case 'images':
        return MOCK_IMAGE_EVIDENCE;
      case 'tables':
        return MOCK_TABLE_EVIDENCE;
      default:
        return [];
    }
  }, [activeTab]);

  /**
   * Simulate loading evidence (placeholder for API call)
   */
  const loadEvidence = useCallback(async () => {
    setIsLoading(true);
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    setIsLoading(false);
  }, []);

  return {
    activeTab,
    setActiveTab,
    evidence: getEvidence(),
    isLoading,
    loadEvidence,
    tabs: [
      { id: 'text', label: 'Text Evidence' },
      { id: 'images', label: 'Images' },
      { id: 'tables', label: 'Tables' }
    ]
  };
}

export default useEvidence;
