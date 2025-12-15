export interface QuestionResponse {
  id: number;
  category: string;
  topic: string;         
  text: string;  
  answer: string;         
  language: string;
  trivia: string |null;
  sourceUrl: string|null;

}