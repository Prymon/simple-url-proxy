import sys
import time
import thread
import threading
from kafka import KafkaProducer, KafkaConsumer
import confluent_kafka

m = 0
mutext = threading.Lock()


def kafka_producer():
    print 'new producer thread\n'
    global m ,mutext
    value = ''
    for i in xrange(1,1000):
        value += 'hello'
    producer = KafkaProducer(bootstrap_servers='10.10.4.49:9092,10.10.4.44:9092', batch_size=100000, acks=0, linger_ms =
            5000)
    for i in xrange(1,10000000):
        producer.send('testTopic',value)
        producer.flush()
        m = m + 1
        if m % 10000 == 0:
            print 'current index:%s' % (m)

    producer.close()

def confluent_kafka_producer():
    print 'new producer thread\n'
    global m ,mutext
    value = ''
    for i in xrange(1,20):
        value += 'hello'
    producer = confluent_kafka.Producer(**{'bootstrap.servers':'10.10.4.49:9092,10.10.4.44:9092'})
    for i in xrange(1,10000000):
        producer.produce('testTopic',value = value)
        #producer.flush()
        if mutext.acquire():
            m = m + 1
            if m % 10000 == 0:
                print 'current index:%s' % (m)
            mutext.release()
        if i % 10000 == 0:
            producer.flush()

def log(str):
    t = time.strftime(r"%Y-%m-%d_%H-%M-%S",time.localtime())
    print("[%s]%s"%(t,str))

def kafka_consumer():
    consumer = KafkaConsumer('testTopic', group_id='20', bootstrap_servers='10.10.4.49:9092',
            auto_offset_reset = 'earliest', enable_auto_commit = True)
    i = 0
    for msg in consumer:
        print 'get message'
        i = i + 1
        recv = "%s:%d:%d: key=%s  index=%d" %(msg.topic,msg.partition,msg.offset,msg.key, i)
        print recv
    consumer.commit()


def mutithread_producer(threadnum):
    for i in xrange(0, threadnum):
        #thread.start_new_thread(kafka_producer, ())
        thread.start_new_thread(confluent_kafka_producer, ())

if __name__ == '__main__':

    if len(sys.argv) >=2 and sys.argv[1] == 'p':
        mutithread_producer(int(sys.argv[2]))
        time.sleep(3600)

    else:
        kafka_consumer()

