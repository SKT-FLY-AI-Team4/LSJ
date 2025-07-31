import React from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// --- 1. 타입 및 데이터 정의 ---

// 채팅 메시지 타입을 명확히 정의
interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
}

// 식사 메뉴 관련 타입 정의
type Meal = {
  name: string;
  description: string;
  emoji: string;
};
type MealCategory = 'today' | 'healthy' | 'lunchbox' | 'allergy';

// 챗봇이 사용할 식사 추천 데이터
const mealRecommendations: Record<MealCategory, Meal[]> = {
  today: [
    { name: '비빔밥', description: '색깔 야채가 가득한 영양 만점 급식!', emoji: '🍚' },
    { name: '된장찌개', description: '따뜻하고 건강한 한식 메뉴!', emoji: '🍲' },
    { name: '잡채', description: '쫄깃한 당면과 야채의 조화!', emoji: '🍜' },
  ],
  healthy: [
    { name: '현미밥', description: '식이섬유가 풍부한 건강한 주식!', emoji: '🍚' },
    { name: '생선구이', description: '단백질과 오메가3가 풍부!', emoji: '🐟' },
    { name: '나물반찬', description: '각종 비타민이 가득한 나물들!', emoji: '🥬' },
  ],
  lunchbox: [
    { name: '김밥 도시락', description: '한 끼 식사로 완벽한 김밥!', emoji: '🍙' },
    { name: '치킨 도시락', description: '아이들이 좋아하는 치킨!', emoji: '🍗' },
    { name: '불고기 도시락', description: '달콤한 불고기와 밥!', emoji: '🥩' },
  ],
  allergy: [
    { name: '알레르기 표시', description: '견과류, 우유, 계란 등 주의 표시를 확인하세요!', emoji: '⚠️' },
    { name: '대체 메뉴', description: '알레르기가 있다면 영양사 선생님께 문의!', emoji: '👨‍⚕️' },
    { name: '안전한 급식', description: '모든 아이들이 안전하게 먹을 수 있어요!', emoji: '✅' },
  ],
};

// 카테고리별 챗봇 초기 응답 메시지
const responses: Record<MealCategory, string> = {
  today: '오늘의 추천 급식 메뉴예요! 영양사 선생님이 특별히 준비하신 메뉴들이에요!',
  healthy: '건강한 급식 메뉴를 추천해드릴게요! 성장기 어린이에게 꼭 필요한 영양소가 가득해요!',
  lunchbox: '맛있는 도시락 메뉴를 준비했어요! 한 끼 식사로 완벽한 구성이에요!',
  allergy: '알레르기 관련 안내해드릴게요! 안전한 급식을 위해 꼭 확인하세요!',
};

// --- 2. 챗봇 로직 함수 ---

// 사용자 입력을 분석하여 카테고리를 결정하는 함수
function analyzeInput(message: string): { category: MealCategory } {
  const msg = message.toLowerCase();
  if (msg.includes('오늘') || msg.includes('추천')) return { category: 'today' };
  if (msg.includes('건강') || msg.includes('영양')) return { category: 'healthy' };
  if (msg.includes('도시락')) return { category: 'lunchbox' };
  if (msg.includes('알레르기') || msg.includes('주의')) return { category: 'allergy' };
  return { category: 'today' }; // 해당하는 키워드가 없으면 기본값 반환
}

// 분석된 카테고리에 맞는 전체 응답 메시지를 생성하는 함수
function generateResponse(analysis: { category: MealCategory }): string {
  let response = responses[analysis.category] + '\n\n';
  const meals = mealRecommendations[analysis.category];

  if (meals) {
    meals.forEach(meal => {
      response += `${meal.emoji} ${meal.name}\n${meal.description}\n\n`;
    });
  }
  return response.trim();
}

// --- 3. React 컴포넌트 ---

export default function ChatScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets(); // 화면의 안전 영역(노치 등) 정보를 가져옴
  const [inputText, setInputText] = React.useState('');
  const [messages, setMessages] = React.useState<Message[]>([
    { id: 1, text: '안녕하세요! 나비에요!\n오늘 메뉴 고민이세요?', sender: 'bot' },
  ]);
  const flatListRef = React.useRef<FlatList>(null);

  // 메시지 전송 처리 함수
  const handleSendMessage = () => {
    if (inputText.trim() === '') return;

    // 1. 사용자 메시지 추가
    const userMessage: Message = { id: Date.now(), text: inputText, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');

    // 2. 챗봇의 응답을 1초 뒤에 추가 (로딩하는 것처럼 보이기 위함)
    setTimeout(() => {
      const analysis = analyzeInput(inputText);
      const botResponseText = generateResponse(analysis);
      const botMessage: Message = { id: Date.now() + 1, text: botResponseText, sender: 'bot' };
      setMessages(prev => [...prev, botMessage]);
    }, 1000);
  };

  // 새 메시지가 추가될 때마다 스크롤을 맨 아래로 이동
  React.useEffect(() => {
    flatListRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  return (
    <View style={styles.modalOverlay}>
      <StatusBar style="light" />
      {/* 배경 클릭 시 뒤로 가기 */}
      <TouchableOpacity style={StyleSheet.absoluteFill} onPress={() => router.back()} />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoidingContainer}
      >
        <View style={styles.chatContainer}>
          {/* 헤더 */}
          <LinearGradient
            colors={['#FFBF00', '#FDD046']}
            style={[styles.chatHeader, { paddingTop: insets.top - 5}]}
          >
            <Text style={styles.chatHeaderTitle}>YUM:AI</Text>
            <TouchableOpacity onPress={() => router.back()}>
              <Text style={styles.closeButton}>&times;</Text>
            </TouchableOpacity>
          </LinearGradient>

          {/* 채팅 메시지 목록 */}
          <FlatList
            ref={flatListRef}
            data={messages}
            style={styles.chatMessages}
            keyExtractor={(item) => item.id.toString()}
            renderItem={({ item }) => (
              <View style={[styles.messageRow, item.sender === 'user' ? styles.userMessageRow : styles.botMessageRow]}>
                {item.sender === 'bot' && (
                  <Image source={require('../assets/images/bot-profile.png')} style={styles.profileImage} />
                )}
                <View style={[styles.messageBubble, item.sender === 'user' ? styles.userMessageBubble : styles.botMessageBubble]}>
                  <Text style={item.sender === 'user' ? styles.userMessageText : styles.botMessageText}>
                    {item.text}
                  </Text>
                </View>
              </View>
            )}
          />

          {/* 입력창 */}
          <View style={[styles.chatInputContainer, { paddingBottom: insets.bottom > 0 ? insets.bottom : 15 }]}>
            <TextInput
              style={styles.chatInput}
              value={inputText}
              onChangeText={setInputText}
              placeholder="얌이에게 물어보세요!"
              multiline={true}
              returnKeyType="send"
              onSubmitEditing={handleSendMessage} // 엔터키로 전송
            />
            <TouchableOpacity style={styles.sendButton} onPress={handleSendMessage}>
              <Text style={styles.sendButtonText}>전송</Text>
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}

// --- 4. 스타일시트 ---

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(190, 190, 190, 0.7)',
  },
  keyboardAvoidingContainer: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  chatContainer: {
    height: '70%',
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    overflow: 'hidden',
  },
  chatHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 15,
  },
  chatHeaderTitle: {
    fontSize: 30,
    fontWeight: 'bold',
  },
  closeButton: {
    fontSize: 30,
    color: '#3C3C32',
  },
  chatMessages: {
    flex: 1,
    backgroundColor: '#FFFBF0',
    padding: 10,
  },
  messageRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginVertical: 8,
  },
  userMessageRow: {
    justifyContent: 'flex-end',
  },
  botMessageRow: {
    justifyContent: 'flex-start',
  },
  profileImage: {
    width: 30,
    height: 40,
    borderRadius: 20,
    marginRight: 8,
  },
  messageBubble: {
    padding: 12,
    borderRadius: 18,
    maxWidth: '75%',
  },
  userMessageBubble: {
    backgroundColor: '#FFBF00',
    borderBottomRightRadius: 4,
  },
  botMessageBubble: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#eee',
    borderBottomLeftRadius: 4,
  },
  userMessageText: {
    color: 'black',
  },
  botMessageText: {
    color: 'black',
  },
  chatInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingTop: 15,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  chatInput: {
    flex: 1,
    backgroundColor: '#f0f0f0',
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderWidth: 0,
    borderRadius: 20,
    marginRight: 10,
    maxHeight: 100,
  },
  sendButton: {
    paddingVertical: 10,
    paddingHorizontal: 15,
    backgroundColor: '#FFBF00',
    borderRadius: 20,
  },
  sendButtonText: {
    fontWeight: 'bold',
  },
});