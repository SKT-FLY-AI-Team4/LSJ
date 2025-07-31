import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// --- 챗봇 데이터 및 로직 ---
const mealRecommendations = {
  today: [
    { name: '비빔밥', description: '색깔 야채가 가득한 영양 만점 급식!', emoji: '🍚' },
    { name: '된장찌개', description: '따뜻하고 건강한 한식 메뉴!', emoji: '🍲' },
    { name: '잡채', description: '쫄깃한 당면과 야채의 조화!', emoji: '🍜' }
  ],
  healthy: [
    { name: '현미밥', description: '식이섬유가 풍부한 건강한 주식!', emoji: '🍚' },
    { name: '생선구이', description: '단백질과 오메가3가 풍부!', emoji: '🐟' },
    { name: '나물반찬', description: '각종 비타민이 가득한 나물들!', emoji: '🥬' }
  ],
  lunchbox: [
    { name: '김밥 도시락', description: '한 끼 식사로 완벽한 김밥!', emoji: '🍙' },
    { name: '치킨 도시락', description: '아이들이 좋아하는 치킨!', emoji: '🍗' },
    { name: '불고기 도시락', description: '달콤한 불고기와 밥!', emoji: '🥩' }
  ],
  allergy: [
    { name: '알레르기 표시', description: '견과류, 우유, 계란 등 주의 표시를 확인하세요!', emoji: '⚠️' },
    { name: '대체 메뉴', description: '알레르기가 있다면 영양사 선생님께 문의!', emoji: '👨‍⚕️' },
    { name: '안전한 급식', description: '모든 아이들이 안전하게 먹을 수 있어요!', emoji: '✅' }
  ]
};

function analyzeInput(message: string) {
  const msg = message.toLowerCase();
  if (msg.includes('오늘') || msg.includes('추천')) return { category: 'today' };
  if (msg.includes('건강') || msg.includes('영양')) return { category: 'healthy' };
  if (msg.includes('도시락')) return { category: 'lunchbox' };
  if (msg.includes('알레르기') || msg.includes('주의')) return { category: 'allergy' };
  return { category: 'today' };
}

function generateResponse(analysis: { category: string }) {
  // 1. responses 객체에 타입을 명시적으로 지정합니다.
  const responses: { [key: string]: string } = {
    today: "오늘의 추천 급식 메뉴예요! 영양사 선생님이 특별히 준비하신 메뉴들이에요!",
    healthy: "건강한 급식 메뉴를 추천해드릴게요! 성장기 어린이에게 꼭 필요한 영양소가 가득해요!",
    lunchbox: "맛있는 도시락 메뉴를 준비했어요! 한 끼 식사로 완벽한 구성이에요!",
    allergy: "알레르기 관련 안내해드릴게요! 안전한 급식을 위해 꼭 확인하세요!"
  };

  // 2. mealRecommendations 객체에도 동일하게 타입을 지정합니다.
  const mealRecommendations: { [key: string]: { name: string; description: string; emoji: string }[] } = {
    today: [
      { name: '비빔밥', description: '색깔 야채가 가득한 영양 만점 급식!', emoji: '🍚' },
      { name: '된장찌개', description: '따뜻하고 건강한 한식 메뉴!', emoji: '🍲' },
      { name: '잡채', description: '쫄깃한 당면과 야채의 조화!', emoji: '🍜' }
    ],
    healthy: [
      { name: '현미밥', description: '식이섬유가 풍부한 건강한 주식!', emoji: '🍚' },
      { name: '생선구이', description: '단백질과 오메가3가 풍부!', emoji: '🐟' },
      { name: '나물반찬', description: '각종 비타민이 가득한 나물들!', emoji: '🥬' }
    ],
    lunchbox: [
      { name: '김밥 도시락', description: '한 끼 식사로 완벽한 김밥!', emoji: '🍙' },
      { name: '치킨 도시락', description: '아이들이 좋아하는 치킨!', emoji: '🍗' },
      { name: '불고기 도시락', description: '달콤한 불고기와 밥!', emoji: '🥩' }
    ],
    allergy: [
      { name: '알레르기 표시', description: '견과류, 우유, 계란 등 주의 표시를 확인하세요!', emoji: '⚠️' },
      { name: '대체 메뉴', description: '알레르기가 있다면 영양사 선생님께 문의!', emoji: '👨‍⚕️' },
      { name: '안전한 급식', description: '모든 아이들이 안전하게 먹을 수 있어요!', emoji: '✅' }
    ]
  };

  let response = responses[analysis.category] + '\n\n';
  const meals = mealRecommendations[analysis.category];
  if (meals) {
    meals.forEach(meal => {
      response += `${meal.emoji} ${meal.name}\n${meal.description}\n\n`;
    });
  }
  return response.trim();
}

// --- React 컴포넌트 ---
export default function ChatScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState([
    { id: 1, text: '안녕하세요! 얌이에요! 🐱\n오늘 급식 메뉴 고민이세요?', sender: 'bot' }
  ]);
  const flatListRef = useRef<FlatList>(null);

  const handleSendMessage = () => {
    if (inputText.trim() === '') return;

    const userMessage = { id: Date.now(), text: inputText, sender: 'user' as const };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');

    setTimeout(() => {
      const analysis = analyzeInput(inputText);
      const botResponseText = generateResponse(analysis);
      const botMessage = { id: Date.now() + 1, text: botResponseText, sender: 'bot' as const };
      setMessages(prev => [...prev, botMessage]);
    }, 1000);
  };

  return (
    <View style={styles.modalOverlay}>
      <StatusBar style="light" />

      {/* 배경 터치를 감지하여 창을 닫는 역할만 하는 투명한 TouchableOpacity */}
      <TouchableOpacity
        style={StyleSheet.absoluteFill}
        onPress={() => router.back()}
      />

      {/* 키보드 및 하단 시스템 바 문제를 해결하는 컨테이너 */}
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoidingContainer}
      >
        {/* 실제 눈에 보이는 채팅창 UI */}
       {/* 실제 눈에 보이는 채팅창 UI */}
        <View style={styles.chatContainer}>
          <LinearGradient colors={['#FFBF00', '#FDD046']} style={[styles.chatHeader, { paddingTop: insets.top + 10 }]}>
            <Text style={styles.chatHeaderTitle}>얌이 음식 도우미</Text>
            <TouchableOpacity onPress={() => router.back()}>
              <Text style={styles.closeButton}>&times;</Text>
            </TouchableOpacity>
          </LinearGradient>
          
          <FlatList
            ref={flatListRef}
            data={messages}
            style={styles.chatMessages}
            keyExtractor={(item) => item.id.toString()}
            renderItem={({ item }) => (
              <View style={[styles.message, item.sender === 'user' ? styles.userMessage : styles.botMessage]}>
                <Text>{item.text}</Text>
              </View>
            )}
            onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
            onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
          />

          <View style={[styles.chatInputContainer, { paddingBottom: insets.bottom > 0 ? insets.bottom : 15 }]}>
            <TextInput
              style={styles.chatInput}
              value={inputText}
              onChangeText={setInputText}
              placeholder="얌이에게 물어보세요!"
              // onSubmitEditing={handleSendMessage}
              multiline={true}
              returnKeyType="send"
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

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  keyboardAvoidingContainer: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  chatContainer: {
    height: '75%',
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
    fontSize: 18,
    fontWeight: 'bold',
  },
  closeButton: {
    fontSize: 30,
  },
  chatMessages: {
    flex: 1,
    backgroundColor: '#FFFBF0',
  },
  message: {
    padding: 12,
    borderRadius: 18,
    marginVertical: 5,
    maxWidth: '80%',
    marginHorizontal: 10,
  },
  userMessage: {
    backgroundColor: '#FFBF00',
    alignSelf: 'flex-end',
  },
  botMessage: {
    backgroundColor: 'white',
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: '#eee',
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
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 20,
    marginRight: 10,
  },
  sendButton: {
    padding: 10,
    backgroundColor: '#FFBF00',
    borderRadius: 20,
  },
  sendButtonText: {
    fontWeight: 'bold',
  },
});